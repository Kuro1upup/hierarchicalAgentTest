from typing import Literal
from IPython.display import Image, display

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from app.agents.supervisorTool import (
    State, create_tavily_tool, scrape_webpages,
    make_supervisor_node, write_document, edit_document, read_document, create_outline, python_repl_tool
)

from dotenv import load_dotenv
# 加载环境变量
load_dotenv()
llm = ChatOpenAI(model="gpt-4o")

def search_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for searching the web using Tavily."""
    tavily_tool = create_tavily_tool()
    search_agent = create_react_agent(llm, tools=[tavily_tool])
    result = search_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="search")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )

def web_scraper_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for scraping web pages."""
    web_scraper_agent = create_react_agent(llm, tools=[scrape_webpages])
    result = web_scraper_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="web_scraper")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )

def doc_writing_node(state: State) -> Command[Literal["supervisor"]]:
    doc_writer_agent = create_react_agent(
        llm,
        tools=[write_document, edit_document, read_document],
        prompt=(
            "You can read, write and edit documents based on note-taker's outlines. "
            "Don't ask follow-up questions."
        ),
    )
    result = doc_writer_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="doc_writer")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )

def note_taking_node(state: State) -> Command[Literal["supervisor"]]:
    note_taking_agent = create_react_agent(
        llm,
        tools=[create_outline, read_document],
        prompt=(
            "You can read documents and create outlines for the document writer. "
            "Don't ask follow-up questions."
        ),
    )
    result = note_taking_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="note_taker")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )

def chart_generating_node(state: State) -> Command[Literal["supervisor"]]:
    chart_generating_agent = create_react_agent(
        llm, tools=[read_document, python_repl_tool]
    )
    result = chart_generating_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=result["messages"][-1].content, name="chart_generator"
                )
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )

def call_research_team(state: State) -> Command[Literal["supervisor"]]:
    # Create research agent
    research_supervisor_node = make_supervisor_node(llm, ["search", "web_scraper"])
    
    research_builder = StateGraph(State)
    research_builder.add_node("supervisor", research_supervisor_node)
    research_builder.add_node("search", search_node)
    research_builder.add_node("web_scraper", web_scraper_node)
    research_builder.add_edge(START, "supervisor")

    research_graph = research_builder.compile()
    display(Image(research_graph.get_graph().draw_mermaid_png()))

    """ Invoke the research team
        This function is called by the supervisor to invoke the research team
        It will call the search and web scraper nodes in sequence"""
    
    response = research_graph.invoke({"messages": state["messages"][-1]})
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response["messages"][-1].content, name="research_team"
                )
            ]
        },
        goto="supervisor",
    )

def call_paper_writing_team(state: State) -> Command[Literal["supervisor"]]:
    # Create document writing agent
    doc_writing_supervisor_node = make_supervisor_node(
        llm, ["doc_writer", "note_taker", "chart_generator"]
    )
    
    paper_writing_builder = StateGraph(State)
    paper_writing_builder.add_node("supervisor", doc_writing_supervisor_node)
    paper_writing_builder.add_node("doc_writer", doc_writing_node)
    paper_writing_builder.add_node("note_taker", note_taking_node)
    paper_writing_builder.add_node("chart_generator", chart_generating_node)
    paper_writing_builder.add_edge(START, "supervisor")

    paper_writing_graph = paper_writing_builder.compile()
    display(Image(paper_writing_graph.get_graph().draw_mermaid_png()))

    """ Invoke the paper writing team
        This function is called by the supervisor to invoke the paper writing team
        It will call the doc writer, note taker and chart generator nodes in sequence"""
    
    response = paper_writing_graph.invoke({"messages": state["messages"][-1]})
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response["messages"][-1].content, name="writing_team"
                )
            ]
        },
        goto="supervisor",
    )

def initialize_supervisor_agent() -> StateGraph:
    """Initialize the supervisor agent with a hierarchical structure."""

    # Create supervisor agent
    teams_supervisor_node = make_supervisor_node(llm, ["research_team", "writing_team"])

    super_builder = StateGraph(State)
    super_builder.add_node("supervisor", teams_supervisor_node)
    super_builder.add_node("research_team", call_research_team)
    super_builder.add_node("writing_team", call_paper_writing_team)
    super_builder.add_edge(START, "supervisor")

    super_graph = super_builder.compile()
    display(Image(super_graph.get_graph().draw_mermaid_png()))
    return super_graph