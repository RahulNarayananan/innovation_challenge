"""
Agent Orchestrator
LangGraph state machine connecting symptom, wearable, and diagnosis agents.
"""
import json
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

from app.agents.symptom_agent import SymptomAgent
from app.agents.wearable_agent import WearableAgent
from app.agents.diagnosis_agent import DiagnosisAgent
from app.agents.llm_provider import get_llm


class AgentState(TypedDict):
    """State that flows through the agent graph."""
    patient_id: str
    user_input: str
    input_type: str  # 'chat', 'wearable', 'check_in'
    symptoms: list
    wearable_alerts: list
    diagnosis: dict
    response: str
    should_diagnose: bool


# ============================================================================
# GRAPH NODES
# ============================================================================

def extract_symptoms(state: AgentState) -> AgentState:
    """Node: Extract symptoms from user input."""
    agent = SymptomAgent()
    result = agent.extract(state['user_input'], state.get('patient_id'))
    state['symptoms'] = result.get('symptoms', [])
    # Trigger diagnosis if any moderate/severe symptoms
    state['should_diagnose'] = any(
        s.get('severity') in ('moderate', 'severe') for s in state['symptoms']
    )
    return state


def check_wearable(state: AgentState) -> AgentState:
    """Node: Check for wearable alerts."""
    agent = WearableAgent()
    # Get recent alerts from buffered readings
    if state.get('wearable_alerts'):
        state['should_diagnose'] = True
    return state


def run_diagnosis(state: AgentState) -> AgentState:
    """Node: Run diagnosis agent if triggered."""
    if not state.get('should_diagnose'):
        return state
    agent = DiagnosisAgent()
    context = f"Patient just reported: {state['user_input']}" if state.get('user_input') else None
    result = agent.assess(state['patient_id'], additional_context=context)
    state['diagnosis'] = result
    return state


def generate_response(state: AgentState) -> AgentState:
    """Node: Generate the final conversational response."""
    llm = get_llm()

    parts = []
    if state.get('symptoms'):
        sym_list = ', '.join(f"{s['name']} ({s['severity']})" for s in state['symptoms'])
        parts.append(f"Extracted symptoms: {sym_list}")
    if state.get('wearable_alerts'):
        for alert in state['wearable_alerts']:
            parts.append(f"Wearable alert: {alert.get('message', alert.get('alert'))}")
    if state.get('diagnosis'):
        d = state['diagnosis']
        parts.append(f"Assessment: {d.get('assessment', '')}")
        parts.append(f"Recovery Score: {d.get('recovery_score', 'N/A')}/100")
        if d.get('call_doctor'):
            parts.append("URGENT: Please contact your oncology team.")
        if d.get('recommendations'):
            parts.append("Recommendations: " + '; '.join(d['recommendations'][:3]))

    context = '\n'.join(parts) if parts else "Normal check-in, no significant concerns."

    prompt = (
        f"Patient said: \"{state.get('user_input', 'check-in')}\"\n\n"
        f"Clinical context:\n{context}\n\n"
        f"Generate a warm, empathetic response (3-5 sentences). "
        f"Acknowledge their symptoms, share relevant insights from the assessment, "
        f"and offer practical advice. If urgent, strongly recommend contacting their care team."
    )

    response = llm.generate(
        prompt=prompt,
        system_prompt=(
            "You are a supportive cancer recovery assistant. "
            "Be warm, empathetic, and grounded in the data. "
            "Never diagnose - only suggest and observe. "
            "Use simple language, avoid medical jargon."
        ),
        temperature=0.7,
    )

    state['response'] = response
    return state


# ============================================================================
# ROUTING
# ============================================================================

def should_diagnose(state: AgentState) -> str:
    """Router: decide whether to run diagnosis."""
    if state.get('should_diagnose'):
        return 'diagnose'
    return 'respond'


# ============================================================================
# BUILD GRAPH
# ============================================================================

def build_chat_graph():
    """Build the LangGraph state machine for chat interactions."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node('extract', extract_symptoms)
    graph.add_node('check_wearable', check_wearable)
    graph.add_node('diagnose', run_diagnosis)
    graph.add_node('respond', generate_response)

    # Set entry point
    graph.set_entry_point('extract')

    # Edges
    graph.add_edge('extract', 'check_wearable')
    graph.add_conditional_edges(
        'check_wearable',
        should_diagnose,
        {'diagnose': 'diagnose', 'respond': 'respond'}
    )
    graph.add_edge('diagnose', 'respond')
    graph.add_edge('respond', END)

    return graph.compile()


# Pre-built graph instance
_chat_graph = None

def get_chat_graph():
    global _chat_graph
    if _chat_graph is None:
        _chat_graph = build_chat_graph()
    return _chat_graph


async def process_chat(patient_id: str, user_input: str) -> dict:
    """Process a chat message through the agent pipeline."""
    try:
        graph = get_chat_graph()
        initial_state = {
            'patient_id': patient_id,
            'user_input': user_input,
            'input_type': 'chat',
            'symptoms': [],
            'wearable_alerts': [],
            'diagnosis': {},
            'response': '',
            'should_diagnose': False,
        }
        result = graph.invoke(initial_state)
        return {
            'response': result.get('response', ''),
            'symptoms': result.get('symptoms', []),
            'diagnosis': result.get('diagnosis', {}),
            'wearable_alerts': result.get('wearable_alerts', []),
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'response': "I'm having trouble processing that request right now. Could you try rephrasing?",
            'error': str(e),
            'symptoms': [],
            'diagnosis': {},
        }
