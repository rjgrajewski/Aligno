import streamlit as st
import pandas as pd
## from streamlit_tags import st_tags

# ---------- Configuration ----------


# CSV file path
CSV_PATH = "justjoinit_offers.csv"


# ---------- Helper functions ----------


@st.cache_data
def load_data(path):
    # Read CSV into DataFrame
    data_frame = pd.read_csv(path)
    # Safety measure: replace empty fields with empty string for safe splitting
    safe_clean = data_frame['Tech Stack'].fillna('')
    # Extract individual skill names from the combined string
    def extract_skills(tech_str):
        skill_names = []
        # Split the string by ';' to separate each skill entry
        for entry in tech_str.split(';'):
            # Only consider entries that contain a colon separating name and level
            if ':' in entry:
                # Take the part before ':'' as the skill name
                name = entry.split(':')[0].strip()
                skill_names.append(name)
        return skill_names

    # Apply the helper function to build a list of skills per row
    data_frame['skills_list'] = safe_clean.apply(extract_skills)
    return data_frame

# Score = (matching_skills + (matching_skills/required_skills))
def match_score(selected_skills, row_skills):
    # If there are no required skills, return 0.0
    if not row_skills:
        return 0.0
    # Count matching skills
    matches = set(selected_skills) & set(row_skills)
    count = len(matches)
    ratio = count / len(row_skills)
    # Return ratio of matches to total required skills
    return count + round(ratio, 2)


# ---------- Main App ----------


st.set_page_config(page_title="Job Finder", layout="wide")
st.title("🔍 Interactive Job Report")

# Initialize session-state keys for selected skills and dropdown
if 'selected_skills' not in st.session_state:
    st.session_state.selected_skills = []
if 'skill_to_add' not in st.session_state:
    st.session_state.skill_to_add = None

data = load_data(CSV_PATH)

# Extract the list of skills lists
skills_nested = data['skills_list']
# Flatten into a single list
flattened_skills = []
for skills in skills_nested:
    for skill in skills:
        flattened_skills.append(skill)
# Deduplicate and sort the skills
unique_skills = set(flattened_skills)
all_skills = sorted(unique_skills)

# Selected skills input
with st.sidebar:
    # 1) First, handle any “remove” request coming back via query-params
    params = st.experimental_get_query_params()
    if "remove" in params:
        for skill in params["remove"]:
            if skill in st.session_state.selected_skills:
                st.session_state.selected_skills.remove(skill)
        # clear them so they don’t stick around
        st.experimental_set_query_params()
        st.experimental_rerun()

    # 2) Now render your badges as HTML links
    st.header("💪 Your skills:")
    if st.session_state.selected_skills:
        badges = '<div style="display:flex;flex-wrap:wrap;gap:8px;padding:4px 0;">'
        for skill in st.session_state.selected_skills:
            badges += (
                f'<a href="?remove={skill}" '
                f'style="'
                  f'background-color:#114f0c;'
                  f'color:#8fff4c;'
                  f'padding:6px 12px;'
                  f'border-radius:6px;'
                  f'text-decoration:none;'
                  f'user-select:none;'
                f'">'
                  f'✕ {skill}'
                f'</a>'
            )
        badges += '</div>'
        st.markdown(badges, unsafe_allow_html=True)
    else:
        st.info("You are awesome! :)")

    available_skills = [s for s in all_skills if s not in st.session_state.selected_skills]
    if available_skills:
        # automatically add skill when selected from dropdown
        def _add_skill():
            skill = st.session_state.skill_to_add
            if skill:
                st.session_state.selected_skills.append(skill)
                # clear dropdown selection
                st.session_state.skill_to_add = None
                st.rerun()

        st.selectbox(
            "What's more? Click to add:",
            available_skills,
            key="skill_to_add",
            on_change=_add_skill
        )
    else:
        st.info("No more skills to add.")
        
 # Pull the currently selected skills from session state
selected_skills = st.session_state.selected_skills
# Filtrowanie i punktacja
data['match_score'] = data['skills_list'].apply(lambda skills: match_score(selected_skills, skills))
filtered = data[data['match_score'] > 0].sort_values(by='match_score', ascending=False)

# Wyświetlenie wyników
st.subheader(f"Found {len(filtered)} matching offers")
if not filtered.empty:
    display_cols = ['ID', 'Job Title', 'Company', 'Location', 'match_score']
    st.dataframe(filtered[display_cols].reset_index(drop=True))
    
    # Rozwijany panel z pełnymi szczegółami
    for _, row in filtered.reset_index(drop=True).iterrows():
        with st.expander(f"{row['Job Title']} @ {row['Company']} (Score: {row['match_score']})"):
            st.write(f"**URL:** {row['Job URL']}")
            st.write(f"**Category:** {row.get('Category', 'N/A')} | **Experience:** {row['Experience']}")
            st.write(f"**Salary B2B:** {row['Salary B2B']} | **Salary Permanent:** {row['Salary Permanent']}")
            st.write(f"**Tech Stack:** {row['Tech Stack']}")
            st.write("---")
else:
    st.info("No offers match your selected skills.")
