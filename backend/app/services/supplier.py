from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Tuple
from backend.app.models import Supplier
from backend.app.schemas import SupplierCreate, SupplierUpdate

class SupplierService:
    @staticmethod
    def get_supplier_by_id(db: Session, supplier_id: int) -> Optional[Supplier]:
        """Fetch a single supplier by its primary key ID."""
        return db.query(Supplier).filter(Supplier.id == supplier_id).first()

    @staticmethod
    def get_suppliers(
        db: Session,
        search: Optional[str] = None,
        country: Optional[str] = None,
        product_name: Optional[str] = None,
        sort_by: str = "id",
        sort_dir: str = "asc",
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Supplier], int]:
        """Fetch list of suppliers with filters, search, sorting and pagination."""
        query = db.query(Supplier)

        # 1. Search filter (checks supplier name, product name, or country)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Supplier.name.ilike(search_pattern),
                    Supplier.product_name.ilike(search_pattern),
                    Supplier.country.ilike(search_pattern)
                )
            )

        # 2. Field-specific filters
        if country:
            query = query.filter(Supplier.country.ilike(country))
        if product_name:
            query = query.filter(Supplier.product_name.ilike(product_name))

        # Count total records matching criteria
        total_count = query.count()

        # 3. Sorting
        sort_col = getattr(Supplier, sort_by, Supplier.id)
        if sort_dir == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())

        # 4. Pagination
        offset = (page - 1) * limit
        suppliers = query.offset(offset).limit(limit).all()

        return suppliers, total_count

    @staticmethod
    def create_supplier(db: Session, supplier_data: SupplierCreate) -> Supplier:
        """Create a new supplier in the database."""
        db_supplier = Supplier(
            name=supplier_data.name,
            country=supplier_data.country,
            product_name=supplier_data.product_name,
            product_cost=supplier_data.product_cost,
            delivery_time=supplier_data.delivery_time,
            quality_rating=supplier_data.quality_rating,
            late_deliveries=supplier_data.late_deliveries,
            experience=supplier_data.experience,
            contact_info=supplier_data.contact_info
        )
        db.add(db_supplier)
        db.commit()
        db.refresh(db_supplier)
        return db_supplier

    @staticmethod
    def update_supplier(db: Session, supplier_id: int, update_data: SupplierUpdate) -> Optional[Supplier]:
        """Update an existing supplier's details."""
        db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not db_supplier:
            return None

        # Apply modifications for fields provided in the update schema
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(db_supplier, key, value)

        db.commit()
        db.refresh(db_supplier)
        return db_supplier

    @staticmethod
    def delete_supplier(db: Session, supplier_id: int) -> bool:
        """Remove a supplier record from the database."""
        db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not db_supplier:
            return False

        db.delete(db_supplier)
        db.commit()
        return True
