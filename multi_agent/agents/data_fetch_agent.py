"""
Data Fetch Agent for retrieving retail data from database.
Handles querying returns, warranties, and product data with filtering and validation.
"""

import asyncio
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from multi_agent.core.base_agent import BaseAgent, AgentConfig
from multi_agent.models.message_types import (
    BaseMessage, MessageType, AgentType, DateRange,
    FetchDataPayload, RawDataPayload, create_message
)
from multi_agent.models.database_models import Product, Return, Warranty, ProductDTO, ReturnDTO, WarrantyDTO
from multi_agent.config.database import db_manager


class DataFetchAgent(BaseAgent):
    """
    Agent responsible for fetching retail data from the database.
    Handles complex queries, filtering, and data validation.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        # Configure for database operations with longer timeout
        fetch_config = config or AgentConfig(
            max_retries=5,
            retry_delay=2.0,
            timeout_seconds=600,  # Longer timeout for large queries
            heartbeat_interval=30
        )
        
        super().__init__(AgentType.DATA_FETCH, fetch_config, "DataFetchAgent")
        
        # Register message handlers
        self.register_handler(MessageType.FETCH_DATA, self.handle_fetch_data)
        
        # Query cache for performance
        self.query_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def _on_start(self):
        """Initialize database connection and validate schema."""
        try:
            # Test database connection
            session = db_manager.get_session()
            try:
                # Verify tables exist and are accessible
                product_count = session.query(Product).count()
                return_count = session.query(Return).count()
                warranty_count = session.query(Warranty).count()
                
                self.logger.info(f"Database connection verified:")
                self.logger.info(f"  Products: {product_count}")
                self.logger.info(f"  Returns: {return_count}")
                self.logger.info(f"  Warranties: {warranty_count}")
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    async def _on_stop(self):
        """Cleanup database connections."""
        self.query_cache.clear()
        self.logger.info("Data fetch agent stopped")
    
    async def handle_fetch_data(self, message: BaseMessage) -> BaseMessage:
        """
        Handle FETCH_DATA message and retrieve data from database.
        """
        try:
            # Parse message payload
            payload = FetchDataPayload(
                date_range=DateRange.from_dict(message.payload["date_range"]),
                tables=message.payload.get("tables", ["returns", "warranties", "products"]),
                filters=message.payload.get("filters", {})
            )
            
            self.logger.info(f"Fetching data for period: {payload.date_range.start} to {payload.date_range.end}")
            
            # Fetch data from database
            data = await self._fetch_data_from_db(payload)
            
            # Validate and prepare response
            response_payload = RawDataPayload(
                returns=data["returns"],
                warranties=data["warranties"],
                products=data["products"],
                metadata=data["metadata"]
            )
            
            # Create response message
            response = create_message(
                MessageType.RAW_DATA,
                self.agent_type,
                AgentType.NORMALIZATION,
                response_payload,
                message.metadata.correlation_id
            )
            
            await self.send_message(response)
            self.logger.info(f"Successfully fetched {len(data['returns'])} returns, {len(data['warranties'])} warranties")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling fetch data: {e}")
            # Send error response
            error_response = self.create_status_message(
                AgentType.COORDINATOR,
                message.metadata.message_id,
                "failed",
                error=str(e)
            )
            await self.send_message(error_response)
            raise
    
    async def _fetch_data_from_db(self, payload: FetchDataPayload) -> Dict[str, Any]:
        """
        Fetch data from database based on payload specifications.
        """
        session = db_manager.get_session()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(payload)
            if cache_key in self.query_cache:
                cached_data, timestamp = self.query_cache[cache_key]
                if (asyncio.get_event_loop().time() - timestamp) < self.cache_ttl:
                    self.logger.debug("Returning cached data")
                    return cached_data
            
            data = {
                "returns": [],
                "warranties": [],
                "products": [],
                "metadata": {}
            }
            
            # Fetch products if requested
            if "products" in payload.tables:
                products = await self._fetch_products(session, payload.filters)
                data["products"] = [ProductDTO(p).__dict__ for p in products]
            
            # Fetch returns if requested
            if "returns" in payload.tables:
                returns = await self._fetch_returns(session, payload.date_range, payload.filters)
                data["returns"] = [ReturnDTO(r).__dict__ for r in returns]
            
            # Fetch warranties if requested
            if "warranties" in payload.tables:
                warranties = await self._fetch_warranties(session, payload.date_range, payload.filters)
                data["warranties"] = [WarrantyDTO(w).__dict__ for w in warranties]
            
            # Generate metadata
            data["metadata"] = self._generate_metadata(data, payload)
            
            # Cache results
            self.query_cache[cache_key] = (data, asyncio.get_event_loop().time())
            
            return data
            
        finally:
            session.close()
    
    async def _fetch_products(self, session: Session, filters: Dict[str, Any]) -> List[Product]:
        """Fetch products with optional filtering."""
        query = session.query(Product)
        
        # Apply filters
        if "product_categories" in filters and filters["product_categories"] != ["all"]:
            query = query.filter(Product.category.in_(filters["product_categories"]))
        
        if "brands" in filters and filters["brands"] != ["all"]:
            query = query.filter(Product.brand.in_(filters["brands"]))
        
        if "price_range" in filters:
            price_min = filters["price_range"].get("min", 0)
            price_max = filters["price_range"].get("max", float('inf'))
            query = query.filter(and_(Product.price >= price_min, Product.price <= price_max))
        
        return query.all()
    
    async def _fetch_returns(self, session: Session, date_range: DateRange, filters: Dict[str, Any]) -> List[Return]:
        """Fetch returns within date range with optional filtering."""
        query = session.query(Return).filter(
            and_(
                Return.return_date >= date_range.start,
                Return.return_date <= date_range.end
            )
        )
        
        # Apply filters
        if "store_locations" in filters and filters["store_locations"] != ["all"]:
            query = query.filter(Return.store_location.in_(filters["store_locations"]))
        
        if "resolution_status" in filters and filters["resolution_status"] != ["all"]:
            query = query.filter(Return.resolution_status.in_(filters["resolution_status"]))
        
        if "product_categories" in filters and filters["product_categories"] != ["all"]:
            query = query.join(Product).filter(Product.category.in_(filters["product_categories"]))
        
        if "amount_range" in filters:
            amount_min = filters["amount_range"].get("min", 0)
            amount_max = filters["amount_range"].get("max", float('inf'))
            query = query.filter(and_(Return.amount >= amount_min, Return.amount <= amount_max))
        
        return query.order_by(Return.return_date.desc()).all()
    
    async def _fetch_warranties(self, session: Session, date_range: DateRange, filters: Dict[str, Any]) -> List[Warranty]:
        """Fetch warranties within date range with optional filtering."""
        query = session.query(Warranty).filter(
            and_(
                Warranty.claim_date >= date_range.start,
                Warranty.claim_date <= date_range.end
            )
        )
        
        # Apply filters
        if "warranty_status" in filters and filters["warranty_status"] != ["all"]:
            query = query.filter(Warranty.status.in_(filters["warranty_status"]))
        
        if "product_categories" in filters and filters["product_categories"] != ["all"]:
            query = query.join(Product).filter(Product.category.in_(filters["product_categories"]))
        
        if "cost_range" in filters:
            cost_min = filters["cost_range"].get("min", 0)
            cost_max = filters["cost_range"].get("max", float('inf'))
            query = query.filter(and_(Warranty.cost >= cost_min, Warranty.cost <= cost_max))
        
        if "resolution_time_range" in filters:
            time_min = filters["resolution_time_range"].get("min", 0)
            time_max = filters["resolution_time_range"].get("max", 999)
            query = query.filter(
                and_(
                    Warranty.resolution_time_days >= time_min,
                    Warranty.resolution_time_days <= time_max
                )
            )
        
        return query.order_by(Warranty.claim_date.desc()).all()
    
    def _generate_metadata(self, data: Dict[str, Any], payload: FetchDataPayload) -> Dict[str, Any]:
        """Generate metadata about the fetched data."""
        metadata = {
            "record_count": sum(len(data[table]) for table in ["returns", "warranties", "products"]),
            "date_range": payload.date_range.to_dict(),
            "query_timestamp": date.today().isoformat(),
            "tables_fetched": payload.tables,
            "filters_applied": payload.filters,
            "data_quality_score": self._calculate_quality_score(data)
        }
        
        # Add table-specific counts
        for table in payload.tables:
            metadata[f"{table}_count"] = len(data.get(table, []))
        
        # Add summary statistics
        if "returns" in data and data["returns"]:
            returns_data = data["returns"]
            metadata["returns_summary"] = {
                "total_amount": sum(r["amount"] for r in returns_data),
                "avg_amount": sum(r["amount"] for r in returns_data) / len(returns_data),
                "unique_products": len(set(r["product_id"] for r in returns_data)),
                "unique_customers": len(set(r["customer_id"] for r in returns_data))
            }
        
        if "warranties" in data and data["warranties"]:
            warranties_data = data["warranties"]
            resolved_warranties = [w for w in warranties_data if w["resolution_time_days"] is not None]
            metadata["warranties_summary"] = {
                "total_cost": sum(w["cost"] for w in warranties_data),
                "avg_cost": sum(w["cost"] for w in warranties_data) / len(warranties_data),
                "avg_resolution_time": sum(w["resolution_time_days"] for w in resolved_warranties) / len(resolved_warranties) if resolved_warranties else 0,
                "resolution_rate": len(resolved_warranties) / len(warranties_data) if warranties_data else 0
            }
        
        return metadata
    
    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate a data quality score based on completeness and consistency."""
        total_records = 0
        quality_issues = 0
        
        # Check returns data quality
        for return_record in data.get("returns", []):
            total_records += 1
            if not return_record.get("reason") or not return_record.get("resolution_status"):
                quality_issues += 1
        
        # Check warranties data quality
        for warranty_record in data.get("warranties", []):
            total_records += 1
            if not warranty_record.get("issue_description") or not warranty_record.get("status"):
                quality_issues += 1
        
        # Check products data quality
        for product_record in data.get("products", []):
            total_records += 1
            if not product_record.get("name") or not product_record.get("category"):
                quality_issues += 1
        
        if total_records == 0:
            return 1.0
        
        return max(0.0, 1.0 - (quality_issues / total_records))
    
    def _generate_cache_key(self, payload: FetchDataPayload) -> str:
        """Generate cache key for query results."""
        import hashlib
        import json
        
        cache_data = {
            "date_range": payload.date_range.to_dict(),
            "tables": sorted(payload.tables),
            "filters": payload.filters
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear the query cache."""
        self.query_cache.clear()
        self.logger.info("Query cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.query_cache),
            "cache_ttl": self.cache_ttl,
            "cache_keys": list(self.query_cache.keys())
        }