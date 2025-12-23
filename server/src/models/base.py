# src/models/base.py

# KHÔNG import từ src.core.database nữa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func

# Định nghĩa Base object TẠI ĐÂY
# Bạn có thể giữ lại hoặc không giữ lại TimestampMixin tùy ý
class TimestampMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

# Base là đối tượng mà tất cả các models của bạn sẽ kế thừa
Base = declarative_base(cls=TimestampMixin)

# Bây giờ, tất cả các models khác (user.py, project.py...) chỉ cần import Base từ tệp này.