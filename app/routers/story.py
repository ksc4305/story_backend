from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import time
import logging

router = APIRouter()

# Mock 데이터 저장소
stories: Dict[str, Dict] = {}


class StoryInitRequest(BaseModel):
    source: str


class StoryResponse(BaseModel):
    story_id: str
    first_sentence: str


class StoryContentRequest(BaseModel):
    sentence: str


class StoryContentResponse(BaseModel):
    options: List[str]


class StoryFinalRequest(BaseModel):
    sentences: List[str]


# 로깅 설정
logging.basicConfig(level=logging.INFO)


# 이야기 초기화 엔드포인트
@router.post("/api/stories/init", response_model=StoryResponse)
async def init_story(request: StoryInitRequest):
    story_id = str(int(time.time()))  # 고유한 story_id 생성 (예: 현재 시간)
    first_sentence = "이것은 생성된 첫 문장입니다."  # Mock 데이터
    stories[story_id] = {
        "story_id": story_id,
        "sentences": [first_sentence],
        "options": {},
    }
    # 입력된 데이터를 터미널에 출력
    logging.info(f"Received story init request: {request.source}")
    logging.info(f"Initialized story: {story_id} with first sentence: {first_sentence}")
    return StoryResponse(story_id=story_id, first_sentence=first_sentence)


# 특정 이야기의 내용 조회 엔드포인트
@router.get(
    "/api/stories/{story_id}/contents/{contents_index}",
    response_model=StoryContentResponse,
)
async def get_story_content(story_id: str, contents_index: int):
    """
    특정 이야기의 특정 페이지 내용을 조회합니다.
    :param story_id: str - 이야기 ID
    :param contents_index: int - 페이지 인덱스
    :return: StoryContentResponse - 선택지 목록
    """
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    story = stories[story_id]
    if contents_index == 1:
        options = [story["sentences"][0]]
    else:
        options = story["options"].get(
            contents_index - 2,
            [
                f"이것은 {contents_index}번째 문장의 첫 번째 선택지입니다.",
                f"이것은 {contents_index}번째 문장의 두 번째 선택지입니다.",
                f"이것은 {contents_index}번째 문장의 세 번째 선택지입니다.",
            ],
        )  # Mock 데이터
    return StoryContentResponse(options=options)


# 특정 이야기의 전체 내용 조회 엔드포인트
@router.get("/api/stories/{story_id}/contents", response_model=Dict[str, List[str]])
async def get_all_story_contents(story_id: str):
    """
    특정 이야기의 전체 내용을 조회합니다.
    :param story_id: str - 이야기 ID
    :return: Dict[str, List[str]] - 전체 문장 목록
    """
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    story = stories[story_id]
    return {"sentences": story["sentences"]}


# 특정 이야기의 내용 추가 엔드포인트
@router.post("/api/stories/{story_id}/contents/{contents_index}")
async def post_story_content(
    story_id: str, contents_index: int, request: StoryContentRequest
):
    """
    특정 이야기의 특정 페이지에 내용을 추가합니다.
    :param story_id: str - 이야기 ID
    :param contents_index: int - 페이지 인덱스
    :param request: StoryContentRequest - 추가할 문장
    :return: dict - 성공 메시지
    """
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    story = stories[story_id]
    story["sentences"].append(request.sentence)
    if contents_index < 10:
        options = [
            f"이것은 {contents_index + 1}번째 문장의 첫 번째 선택지입니다.",
            f"이것은 {contents_index + 1}번째 문장의 두 번째 선택지입니다.",
            f"이것은 {contents_index + 1}번째 문장의 세 번째 선택지입니다.",
        ]  # Mock 데이터
        story["options"][contents_index] = options
    # 입력된 데이터를 터미널에 출력
    logging.info(
        f"Received story content request for story_id: {story_id}, contents_index: {contents_index}"
    )
    logging.info(f"Appended sentence: {request.sentence}")
    return {"message": "Success"}


# 이야기 최종 결정 엔드포인트
@router.post("/api/stories/{story_id}/contents/final")
async def finalize_story_content(story_id: str, request: StoryFinalRequest):
    """
    특정 이야기의 최종 내용을 결정합니다.
    :param story_id: str - 이야기 ID
    :param request: StoryFinalRequest - 최종 문장 목록
    :return: dict - 성공 메시지
    """
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    story = stories[story_id]
    story["final_sentences"] = request.sentences
    # 입력된 데이터를 터미널에 출력
    logging.info(f"Finalized story content for story_id: {story_id}")
    logging.info(f"Final sentences: {request.sentences}")
    return {"message": "Story finalized successfully"}


# 저장된 이야기 전체 조회 엔드포인트 (디버그용)
@router.get("/api/stories", response_model=Dict[str, Dict])
async def get_all_stories():
    """
    저장된 모든 이야기를 조회합니다. 디버그 용도로 사용됩니다.
    :return: dict - 모든 이야기 데이터
    """
    return stories
