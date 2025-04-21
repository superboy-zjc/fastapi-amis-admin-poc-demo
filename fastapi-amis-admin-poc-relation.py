from typing import Optional
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from fastapi_amis_admin.crud import SqlalchemyCrud
from pydantic import BaseModel
from typing import Optional
from fastapi_amis_admin.crud.parser import TableModelParser
import tests.models.sqla as models


content_schema = TableModelParser.get_table_model_schema(models.ArticleContent)

# 1. Create Model
class ArticleUpdate(BaseModel):
    title: str = None
    description: str = None
    content: Optional[content_schema] = None  # Relationship

class ArticleCrud(SqlalchemyCrud):
    router_prefix = "/article"
    update_exclude = {"content": {"id"}}
    schema_update = ArticleUpdate
    
# 2. Create AsyncEngine
database_url = 'sqlite+aiosqlite:///amisadmin.db'
engine: AsyncEngine = create_async_engine(database_url, future=True)

# 3. Register crud route
ins = ArticleCrud(models.Article, engine).register_crud()

app = FastAPI(debug=True)

# 4. Include the router
app.include_router(ins.router)

# 5. Create model database table (first run)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
    