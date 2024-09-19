from datetime import date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from database import engine


class Base(DeclarativeBase):
  pass


class Expense(Base):
  __tablename__ = 'expense'

  id: Mapped[int] = mapped_column(primary_key=True)
  amount: Mapped[float]
  category: Mapped[str]
  date: Mapped[date]
  description: Mapped[str] = mapped_column(nullable=True)

  def __repr__(self) -> str:
    return f"<Expense(id={self.id}, amount={self.amount}, category={self.category}, date={self.date}, description={self.description})"

Base.metadata.create_all(engine)