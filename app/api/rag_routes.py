from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.generation.models import RagResponse
from app.generation.service import RagGenerationError
from app.retrieval.models import SearchFilters
from app.schemas.rag import RagEvidenceResponse,RagQueryRequest,RagQueryResponse
from app.services.rag_application import RagServiceConfigurationError,check_rag_ready,get_rag_service
router=APIRouter(prefix='/api',tags=['RAG'])
def _to_response(response:RagResponse)->RagQueryResponse:
    return RagQueryResponse(query=response.query,answer=response.answer,used_chunk_ids=response.used_chunk_ids,evidence=[RagEvidenceResponse(evidence_id=item.evidence_id,chunk_id=item.result.chunk_id,document_id=item.result.document_id,text=item.result.text,score=item.result.score,page=item.result.page,filename=item.result.filename,document_type=item.result.document_type,title=item.result.title,issue_date=item.result.issue_date,effective_date=item.result.effective_date,status=item.result.status,version=item.result.version) for item in response.evidence])
@router.post('/query',response_model=RagQueryResponse)
def query_compliance(request:RagQueryRequest)->RagQueryResponse:
    try:
        filters=SearchFilters(document_type=request.document_type,status=request.status,document_id=request.document_id,version=request.version,effective_date=request.effective_date.isoformat() if request.effective_date else None); return _to_response(get_rag_service().answer(request.question,top_k=request.top_k,filters=filters,as_of_date=request.as_of_date))
    except RagServiceConfigurationError as exc: raise HTTPException(status_code=503,detail='RAG service is not configured') from exc
    except ValueError as exc: raise HTTPException(status_code=400,detail=str(exc)) from exc
    except RagGenerationError as exc: raise HTTPException(status_code=502,detail='compliance answer generation failed') from exc
    except Exception as exc: raise HTTPException(status_code=500,detail='unexpected compliance query failure') from exc
@router.get('/rag/ready')
def rag_readiness():
    try: check_rag_ready()
    except Exception as exc: raise HTTPException(status_code=503,detail='local RAG inference is not ready') from exc
    return {'status':'ready'}
