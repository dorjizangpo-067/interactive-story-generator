from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.orm import Session

from models.story import Story, StoryNode

from .config import settings
from .models import StoryLLMResponse, StoryNodeLLM, StoryOptionLLM
from .promps import STORY_PROMPT


class StoryGenerator:
    @classmethod
    def _get_llm(cls):
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # or "gemini-2.5-pro"
            google_api_key=settings.GOOGLE_API_KEY.get_secret_value(),
        )

    @classmethod
    def generate_story(
        cls, db: Session, session_id: str, theme: str = "fantasy"
    ) -> Story:
        llm = cls._get_llm()
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", STORY_PROMPT),
                ("human", f"Create a story with this theme:{theme}"),
            ]
        ).partial(format_instructions=story_parser.get_format_instructions())

        raw_response = llm.invoke(prompt.invoke({}))

        response_text = raw_response.content

        if not hasattr(raw_response, "content"):
            raise ValueError("LLM response has no content")

        response_text = raw_response.content
        if not isinstance(response_text, str):
            raise ValueError(
                "Expected string response from LLM, got structured content"
            )

        story_structure = story_parser.parse(response_text)

        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush()

        root_node_data = story_structure.rootNode

        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)

        db.commit()

        return story_db

    @classmethod
    def _process_story_node(
        cls,
        db: Session,
        story_id: int,
        node_data: StoryNodeLLM | dict,
        is_root: bool = False,
    ) -> StoryNode:

        content = (
            node_data.content
            if isinstance(node_data, StoryNodeLLM)
            else node_data["content"]
        )
        is_ending = (
            node_data.isEnding
            if isinstance(node_data, StoryNodeLLM)
            else node_data["isEnding"]
        )
        is_winning_ending = (
            node_data.isWinningEnding
            if isinstance(node_data, StoryNodeLLM)
            else node_data["isWinningEnding"]
        )

        node = StoryNode(
            story_id=story_id,
            content=content,
            is_root=is_root,
            is_ending=is_ending,
            is_winning_ending=is_winning_ending,
            options=[],
        )
        db.add(node)
        db.flush()

        if not node.is_ending:
            options = (
                node_data.options
                if isinstance(node_data, StoryNodeLLM)
                else node_data.get("options")
            )

            if options:
                option_list = []
                for option_data in options:
                    next_node = (
                        option_data.nextNode
                        if isinstance(option_data, StoryOptionLLM)
                        else option_data["nextNode"]
                    )

                    if isinstance(next_node, dict):
                        next_node = StoryNodeLLM.model_validate(next_node)

                    child_node = cls._process_story_node(db, story_id, next_node, False)

                    option_list.append(
                        {
                            "text": option_data.text,
                            "node_id": child_node.id,
                        }
                    )
                node.options = option_list

        db.flush()
        return node
