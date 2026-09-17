import streamlit as st
import os
import json

from dotenv import load_dotenv
from google import genai

from rag import retrieve_knowledge


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY not found in .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="BioDiversify AI",
    page_icon="🌿",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.title {
    font-size: 42px;
    font-weight: 700;
}

.subtitle {
    font-size: 18px;
    color: #666;
}

.metric-card {
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-bottom: 10px;
}

.recommendation {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">🌿 BioIntel AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered biodiversity intelligence and environmental reasoning system'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "environment" not in st.session_state:
    st.session_state.environment = {}


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🌍 Environmental Profile")

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    region = st.text_input(
        "Region",
        placeholder="e.g. Maharashtra, India"
    )

    # --------------------------------------------------------
    # SOIL
    # --------------------------------------------------------

    st.subheader("🌱 Soil")

    soil_ph = st.number_input(
        "Soil pH",
        min_value=0.0,
        max_value=14.0,
        value=7.0,
        step=0.1
    )

    soil_carbon = st.number_input(
        "Soil Organic Carbon (%)",
        min_value=0.0,
        max_value=20.0,
        value=1.0,
        step=0.1
    )

    soil_moisture = st.number_input(
        "Soil Moisture (%)",
        min_value=0.0,
        max_value=100.0,
        value=30.0,
        step=1.0
    )

    # --------------------------------------------------------
    # CLIMATE
    # --------------------------------------------------------

    st.subheader("🌦️ Climate")

    rainfall = st.number_input(
        "Annual Rainfall (mm)",
        min_value=0.0,
        max_value=10000.0,
        value=800.0,
        step=50.0
    )

    temperature = st.number_input(
        "Average Temperature (°C)",
        min_value=-20.0,
        max_value=60.0,
        value=25.0,
        step=0.5
    )

    # --------------------------------------------------------
    # LAND USE
    # --------------------------------------------------------

    st.subheader("🌾 Land")

    land_use = st.selectbox(
        "Land Use",
        [
            "Monoculture",
            "Mixed Cropping",
            "Agroforestry",
            "Forest",
            "Grassland",
            "Wetland",
            "Urban",
            "Other"
        ]
    )

    crop = st.text_input(
        "Main Crop / Vegetation",
        placeholder="e.g. Wheat"
    )

    # --------------------------------------------------------
    # BIODIVERSITY
    # --------------------------------------------------------

    st.subheader("🦋 Biodiversity")

    species_richness = st.number_input(
        "Observed Species Richness",
        min_value=0,
        max_value=10000,
        value=10,
        step=1,
        help="Approximate number of different species observed."
    )

    habitat_diversity = st.slider(
        "Habitat Diversity",
        min_value=1,
        max_value=10,
        value=3,
        help="1 = very low habitat diversity, 10 = very high."
    )

    # --------------------------------------------------------
    # HUMAN PRESSURE
    # --------------------------------------------------------

    st.subheader("🏭 Human Pressure")

    pesticide = st.selectbox(
        "Pesticide Pressure",
        [
            "Low",
            "Medium",
            "High"
        ]
    )

    deforestation = st.selectbox(
        "Deforestation / Habitat Loss",
        [
            "Low",
            "Medium",
            "High"
        ]
    )

    pollution = st.selectbox(
        "Pollution Pressure",
        [
            "Low",
            "Medium",
            "High"
        ]
    )

    st.divider()

    if st.button("🔄 Clear Conversation"):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# STORE ENVIRONMENTAL DATA
# ============================================================

st.session_state.environment = {

    "region": region,

    "soil": {
        "pH": soil_ph,
        "organic_carbon_percent": soil_carbon,
        "moisture_percent": soil_moisture
    },

    "climate": {
        "annual_rainfall_mm": rainfall,
        "average_temperature_c": temperature
    },

    "land_use": land_use,

    "crop": crop,

    "biodiversity": {
        "species_richness": species_richness,
        "habitat_diversity": habitat_diversity
    },

    "human_pressure": {
        "pesticide": pesticide,
        "deforestation": deforestation,
        "pollution": pollution
    }
}


# ============================================================
# BIODIVERSITY PRESSURE SCORE
# ============================================================

def calculate_risk_score():

    score = 0
    factors = []

    env = st.session_state.environment

    soil = env["soil"]
    climate = env["climate"]
    human = env["human_pressure"]
    biodiversity = env["biodiversity"]

    # --------------------------------------------------------
    # Soil organic carbon
    # --------------------------------------------------------

    if soil["organic_carbon_percent"] < 0.5:

        score += 1

        factors.append(
            "Very low soil organic carbon"
        )

    elif soil["organic_carbon_percent"] < 1:

        score += 1

        factors.append(
            "Low soil organic carbon"
        )

    # --------------------------------------------------------
    # Soil moisture
    # --------------------------------------------------------

    if soil["moisture_percent"] < 20:

        score += 1

        factors.append(
            "Low soil moisture"
        )

    # --------------------------------------------------------
    # Rainfall
    # --------------------------------------------------------

    if climate["annual_rainfall_mm"] < 600:

        score += 1

        factors.append(
            "Low rainfall"
        )

    # --------------------------------------------------------
    # Land use
    # --------------------------------------------------------

    if env["land_use"] == "Monoculture":

        score += 1

        factors.append(
            "Monoculture land use"
        )

    # --------------------------------------------------------
    # Biodiversity
    # --------------------------------------------------------

    if biodiversity["species_richness"] < 5:

        score += 1

        factors.append(
            "Low observed species richness"
        )

    if biodiversity["habitat_diversity"] <= 2:

        score += 1

        factors.append(
            "Low habitat diversity"
        )

    # --------------------------------------------------------
    # Human pressures
    # --------------------------------------------------------

    if human["pesticide"] == "High":

        score += 1

        factors.append(
            "High pesticide pressure"
        )

    if human["pollution"] == "High":

        score += 1

        factors.append(
            "High pollution pressure"
        )

    if human["deforestation"] == "High":

        score += 1

        factors.append(
            "High habitat-loss pressure"
        )

    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    # Maximum possible score is 9

    if score <= 2:

        risk = "Low"

    elif score <= 5:

        risk = "Moderate"

    else:

        risk = "High"

    return score, risk, factors


# ============================================================
# MISSING DATA CHECK
# ============================================================

def check_missing_data():

    env = st.session_state.environment

    missing = []

    if not env["region"].strip():

        missing.append("region")

    if not env["crop"].strip():

        missing.append("main crop or vegetation")

    if env["biodiversity"]["species_richness"] <= 0:

        missing.append(
            "observed species richness"
        )

    return missing


# ============================================================
# RETRIEVE ENVIRONMENTAL KNOWLEDGE
# ============================================================

def retrieve_environmental_knowledge(query):

    try:

        results = retrieve_knowledge(
            query,
            n_results=6
        )

        knowledge = []

        for document, metadata in results:

            knowledge.append({

                "source": metadata.get(
                    "source",
                    "Unknown"
                ),

                "file": metadata.get(
                    "file",
                    "Unknown"
                ),

                "type": metadata.get(
                    "type",
                    "Unknown"
                ),

                "content": document
            })

        return knowledge

    except Exception as e:

        st.error(
            f"RAG retrieval error: {e}"
        )

        return []


# ============================================================
# ENVIRONMENT CONTEXT
# ============================================================

def build_environment_context():

    return json.dumps(
        st.session_state.environment,
        indent=2
    )


# ============================================================
# CREATE GEMINI PROMPT
# ============================================================

def create_prompt(
    user_question,
    retrieved_knowledge
):

    knowledge_text = ""

    for i, item in enumerate(
        retrieved_knowledge,
        start=1
    ):

        knowledge_text += f"""
EVIDENCE {i}

Source category:
{item.get("source", "Unknown")}

Source file:
{item.get("file", "Unknown")}

Evidence type:
{item.get("type", "Unknown")}

Content:
{item.get("content", "")}

--------------------------------------------------
"""

    environment = build_environment_context()

    prompt = f"""

You are BioIntel AI, an environmental scientist and
biodiversity decision-support system.

Your job is to reason about biodiversity using multiple
environmental variables simultaneously.

===========================================================
IMPORTANT RULES
===========================================================

1. Do NOT give generic environmental advice.

2. Use the environmental profile provided below.

3. Connect AT LEAST THREE environmental variables in your
reasoning.

4. Every recommendation must explain:

   - What should be done
   - Why it works scientifically
   - Which environmental metrics may improve
   - How those metrics interact
   - Expected time horizon
   - Evidence/source used

5. Do not invent scientific studies.

6. Do not invent numerical improvement percentages.

7. Do not invent citations, DOI numbers, publication years,
or study names.

8. If the retrieved knowledge does not contain a quantitative
estimate, explicitly say that an exact numerical estimate
cannot be established from the available evidence.

9. Clearly distinguish:

   Evidence
   Reasoning / inference
   Recommendation

10. Consider interactions between:

   - Soil health
   - Soil organic carbon
   - Soil moisture
   - Biodiversity
   - Climate
   - Rainfall
   - Temperature
   - Land use
   - Habitat diversity
   - Human pressure

11. Build a causal chain before recommending an intervention.

12. Identify environmental constraints first.

13. Explicitly connect at least THREE variables.

Examples:

Soil organic carbon
→ water retention
→ vegetation stress
→ habitat quality

Rainfall
→ soil moisture
→ plant productivity
→ species survival

Monoculture
→ habitat simplification
→ lower resource diversity
→ biodiversity pressure

Habitat fragmentation
→ reduced movement
→ population isolation
→ climate vulnerability

14. Do not simply list independent effects.

15. Explain how changing one environmental variable can
influence another.

16. Prefer interventions that address multiple environmental
pressures simultaneously.

17. Do not claim that an intervention will definitely improve
biodiversity.

Use:

"may"
"can"
"is expected to"

when effects depend on context.

18. Use ONLY the retrieved knowledge to support scientific claims.

19. For every recommendation, identify the retrieved evidence
that supports it.

20. If evidence is indirect, explicitly identify the statement
as an inference.

21. Do not fabricate numerical improvement estimates.

22. Recommendations should be measurable.

23. Suggest indicators that the user can monitor over time.

24. Consider trade-offs.

25. Consider the specific environmental profile rather than
giving the same answer for every ecosystem.

===========================================================
ENVIRONMENTAL PROFILE
===========================================================

{environment}

===========================================================
RETRIEVED SCIENTIFIC KNOWLEDGE
===========================================================

{knowledge_text}

===========================================================
USER QUESTION
===========================================================

{user_question}

===========================================================
REQUIRED RESPONSE FORMAT
===========================================================

## 🌿 Environmental Diagnosis

Briefly identify the major ecological pressures.

Mention the environmental variables responsible.

--------------------------------------------------

## 🔗 Multi-Metric Reasoning

Explain the causal relationships between at least
THREE environmental variables.

Use arrows where useful.

Example:

Low rainfall
→ low soil moisture
→ vegetation stress
→ reduced habitat resources

--------------------------------------------------

## 🎯 Recommended Actions

Give 2–4 actionable recommendations.

For each:

### Recommendation 1

**What to do:**

Clearly describe the intervention.

**Why it works:**

Explain the scientific mechanism.

**Multi-metric effect:**

Explain how at least THREE environmental variables
are connected.

**Impacted metrics:**

List measurable environmental indicators.

**Time horizon:**

Short term:
...

Medium term:
...

Long term:
...

**Evidence:**

Identify the retrieved source category/file.

--------------------------------------------------

### Recommendation 2

Use the same structure.

--------------------------------------------------

## 📊 Metrics to Monitor

Give measurable indicators.

Examples:

- Soil organic carbon (%)
- Soil moisture (%)
- Soil pH
- Vegetation cover (%)
- Species richness
- Habitat diversity
- Pollinator observations
- Water availability
- Pesticide pressure

--------------------------------------------------

## ⏳ Expected Timeline

### Short term

0–6 months

### Medium term

6–24 months

### Long term

2+ years

--------------------------------------------------

## ⚠️ Risks and Uncertainty

Explain:

- Evidence limitations
- Local environmental variation
- Possible trade-offs
- Management dependencies
- Any missing information

--------------------------------------------------

## 📚 Knowledge Sources

List ONLY the source categories/files actually used
from the retrieved knowledge.

Do not invent sources.

"""

    return prompt


# ============================================================
# GEMINI RESPONSE
# ============================================================

def generate_response(prompt):

    # Try models in order
    models = [
        "gemini-3.6-flash",
        "gemini-3.6-flash-lite"
    ]

    last_error = None

    for model_name in models:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response and response.text:

                    return response.text

            except Exception as e:

                last_error = str(e)

                # Wait before retrying
                import time

                time.sleep(2)

    return f"""
### ⚠️ Gemini Service Temporarily Unavailable

The biodiversity knowledge retrieval system worked,
but the Gemini reasoning service is temporarily unavailable.

**Error:**
{last_error}

Please try the question again in a few seconds.
"""


# ============================================================
# ANALYZE QUESTION
# ============================================================

def analyze_question(question):

    # --------------------------------------------------------
    # Check missing information
    # --------------------------------------------------------

    missing = check_missing_data()

    if missing:

        return (
            "### 🔎 I need a little more information\n\n"
            "Before making a reliable biodiversity assessment, "
            "please provide:\n\n"
            + "\n".join(
                f"- **{item}**"
                for item in missing
            )
            + "\n\n"
            "This helps me connect the environmental variables "
            "rather than giving a generic recommendation."
        )

    # --------------------------------------------------------
    # Retrieve knowledge
    # --------------------------------------------------------

    retrieved = retrieve_environmental_knowledge(
        question
    )

    if not retrieved:

        return (
            "I could not retrieve relevant scientific evidence "
            "from the biodiversity knowledge base."
        )

    # --------------------------------------------------------
    # Create prompt
    # --------------------------------------------------------

    prompt = create_prompt(
        question,
        retrieved
    )

    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    return generate_response(
        prompt
    )


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "💬 Environmental Scientist",
        "📊 Environmental Profile",
        "🧪 What-If Analysis"
    ]
)


# ============================================================
# TAB 1 — CHATBOT
# ============================================================

with tab1:

    st.subheader(
        "Ask about your ecosystem"
    )

    st.caption(
        "Describe your biodiversity, soil, climate, "
        "land-use, or environmental problem."
    )

    # --------------------------------------------------------
    # Display previous messages
    # --------------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # --------------------------------------------------------
    # Chat input
    # --------------------------------------------------------

    user_question = st.chat_input(
        "Example: My land has low soil carbon and declining biodiversity..."
    )

    if user_question:

        # ----------------------------------------------------
        # User message
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_question
            }
        )

        with st.chat_message("user"):

            st.markdown(
                user_question
            )

        # ----------------------------------------------------
        # AI response
        # ----------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "Retrieving scientific evidence and reasoning..."
            ):

                answer = analyze_question(
                    user_question
                )

            st.markdown(
                answer
            )

        # ----------------------------------------------------
        # Save response
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


# ============================================================
# TAB 2 — ENVIRONMENTAL PROFILE
# ============================================================

with tab2:

    st.subheader(
        "🌍 Current Environmental Profile"
    )

    env = st.session_state.environment

    # --------------------------------------------------------
    # Biodiversity pressure
    # --------------------------------------------------------

    score, risk, factors = calculate_risk_score()

    st.subheader(
        "🌱 Biodiversity Pressure Assessment"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Ecological Pressure Score",
            f"{score}/9"
        )

    with col2:

        st.metric(
            "Pressure Level",
            risk
        )

    with col3:

        st.metric(
            "Species Richness",
            env["biodiversity"]["species_richness"]
        )

    st.caption(
        "Prototype ecological pressure screening score. "
        "This is NOT a validated biodiversity index."
    )

    if factors:

        st.write(
            "**Main contributing factors:**"
        )

        for factor in factors:

            st.write(
                f"• {factor}"
            )

    else:

        st.success(
            "No major pressure factors were detected "
            "by the prototype screening rules."
        )

    st.divider()

    # --------------------------------------------------------
    # SOIL
    # --------------------------------------------------------

    st.subheader("🌱 Soil Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Soil pH",
            env["soil"]["pH"]
        )

    with col2:

        st.metric(
            "Organic Carbon",
            f"{env['soil']['organic_carbon_percent']}%"
        )

    with col3:

        st.metric(
            "Soil Moisture",
            f"{env['soil']['moisture_percent']}%"
        )

    # --------------------------------------------------------
    # CLIMATE
    # --------------------------------------------------------

    st.subheader("🌦️ Climate Metrics")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Annual Rainfall",
            f"{env['climate']['annual_rainfall_mm']} mm"
        )

    with col2:

        st.metric(
            "Average Temperature",
            f"{env['climate']['average_temperature_c']} °C"
        )

    # --------------------------------------------------------
    # LAND
    # --------------------------------------------------------

    st.subheader("🌾 Land Use")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Land Use",
            env["land_use"]
        )

    with col2:

        st.metric(
            "Main Crop",
            env["crop"] if env["crop"] else "Not provided"
        )

    # --------------------------------------------------------
    # BIODIVERSITY
    # --------------------------------------------------------

    st.subheader("🦋 Biodiversity Indicators")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Species Richness",
            env["biodiversity"]["species_richness"]
        )

    with col2:

        st.metric(
            "Habitat Diversity",
            f"{env['biodiversity']['habitat_diversity']}/10"
        )

    # --------------------------------------------------------
    # HUMAN PRESSURE
    # --------------------------------------------------------

    st.subheader("🏭 Human Pressure")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Pesticide",
            env["human_pressure"]["pesticide"]
        )

    with col2:

        st.metric(
            "Deforestation",
            env["human_pressure"]["deforestation"]
        )

    with col3:

        st.metric(
            "Pollution",
            env["human_pressure"]["pollution"]
        )

    st.divider()

    # --------------------------------------------------------
    # Structured data
    # --------------------------------------------------------

    st.subheader(
        "Structured Environmental Data"
    )

    st.json(
        env
    )


# ============================================================
# TAB 3 — WHAT IF ANALYSIS
# ============================================================

with tab3:

    st.subheader(
        "🧪 What-If Biodiversity Analysis"
    )

    st.write(
        "Compare your current environmental condition "
        "with a proposed intervention."
    )

    intervention = st.selectbox(
        "Select intervention",
        [
            "Introduce cover crops",
            "Introduce intercropping",
            "Introduce agroforestry",
            "Reduce pesticide pressure",
            "Add flowering field margins",
            "Restore habitat connectivity",
            "Increase soil organic matter",
            "Create water retention zones"
        ]
    )

    if st.button(
        "🔬 Analyze Intervention"
    ):

        current_environment = (
            build_environment_context()
        )

        question = f"""

Current environmental condition:

{current_environment}

Proposed intervention:

{intervention}

Analyze this intervention as an environmental
decision-support problem.

==================================================
REQUIRED ANALYSIS
==================================================

1. Identify the current environmental constraints.

2. Explain the ecological mechanism of the intervention.

3. Connect at least THREE environmental variables.

4. Explain effects on:

- Soil
- Water
- Climate
- Land use
- Biodiversity
- Human pressure

where relevant.

5. Identify measurable environmental metrics.

6. Give:

Short-term effects
Medium-term effects
Long-term effects

7. Identify possible trade-offs.

8. Identify conditions required for success.

9. Use the retrieved scientific knowledge.

10. Do not invent numerical estimates.

11. Distinguish evidence from inference.

12. Identify the source files used.

"""

        with st.spinner(
            "Running multi-metric environmental analysis..."
        ):

            answer = analyze_question(
                question
            )

        st.markdown(
            answer
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "BioIntel AI | RAG-grounded biodiversity decision support system"
)