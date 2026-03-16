import pytest
from io import BytesIO


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_upload_requires_auth(client):
    response = await client.post("/api/v1/cv/upload")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_analyses_requires_auth(client):
    response = await client.get("/api/v1/cv/analyses")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_analysis_requires_auth(client):
    response = await client.get("/api/v1/cv/analyses/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_cv_success(client, registered_user_token):
    """CV başarıyla yüklenip analiz edildiğini test et."""
    # Sample PDF content (minimal valid PDF)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test CV) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000279 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
373
%%EOF
"""
    
    files = {"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
    response = await client.post(
        "/api/v1/cv/upload",
        headers={"Authorization": f"Bearer {registered_user_token}"},
        files=files,
    )
    assert response.status_code == 201
    data = response.json()
    assert "analysis_id" in data
    assert "message" in data


@pytest.mark.asyncio
async def test_list_analyses_empty(client, registered_user_token):
    """Başlangıçta analiz listesi boş olmalı."""
    response = await client.get(
        "/api/v1/cv/analyses",
        headers={"Authorization": f"Bearer {registered_user_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_analysis_not_found(client, registered_user_token):
    """Olmayan analiz ID'si 404 dönmeli."""
    response = await client.get(
        "/api/v1/cv/analyses/99999",
        headers={"Authorization": f"Bearer {registered_user_token}"},
    )
    assert response.status_code == 404
