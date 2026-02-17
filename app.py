"""
MPT Survey — Public Post-Meeting Survey App
No authentication required - accessed via unique links
"""
import streamlit as st
from datetime import datetime
from supabase import create_client
import os

# Page config
st.set_page_config(
    page_title="Meeting Feedback | Metro Point Technology",
    page_icon="📋",
    layout="centered"
)

# Custom CSS for clean survey experience
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stButton > button { width: 100%; }
    
    /* Style multiselect dropdown to be more visible */
    .stMultiSelect [data-baseweb="select"] {
        background-color: #f8f9fa;
        border: 2px solid #dc3545 !important;
        border-radius: 8px;
    }
    
    /* Dropdown menu styling */
    .stMultiSelect [data-baseweb="popover"] {
        background-color: #f8f9fa !important;
        border: 2px solid #dc3545 !important;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.2);
    }
    
    /* Option items in dropdown */
    .stMultiSelect [role="listbox"] {
        background-color: #f8f9fa !important;
    }
    
    .stMultiSelect [role="option"] {
        padding: 10px 12px;
        border-bottom: 1px solid #e9ecef;
    }
    
    .stMultiSelect [role="option"]:hover {
        background-color: #ffe6e6 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase (CRM database)
@st.cache_resource
def get_supabase():
    url = os.getenv("SUPABASE_URL", st.secrets.get("SUPABASE_URL", ""))
    key = os.getenv("SUPABASE_ANON_KEY", st.secrets.get("SUPABASE_ANON_KEY", ""))
    return create_client(url, key)

supabase = get_supabase()

# Get query parameters
params = st.query_params
contact_id = params.get("contact_id", "")
survey_type = params.get("type", "attendee")  # "attendee" or "host"
meeting_date = params.get("date", datetime.now().strftime("%Y-%m-%d"))

# Header with logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("mpt-logo.png", width=400)

st.title("📋 Meeting Feedback")

if not contact_id:
    st.error("⚠️ Invalid survey link. Please use the link from your email.")
    st.info("If you believe this is an error, please contact support@metropointtech.com")
    st.stop()

# Get contact info
try:
    response = supabase.table("contacts").select("first_name, last_name, company").eq("id", contact_id).single().execute()
    contact = response.data
    if not contact:
        st.error("⚠️ Contact not found. The survey link may have expired.")
        st.stop()
    contact_name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
    company = contact.get('company', '')
except Exception as e:
    st.error("⚠️ Could not load survey. Please try again later.")
    st.stop()

# Check if already submitted (optional - could add a survey_responses table)
# For now, allow multiple submissions (they append to notes)

st.markdown("---")

# ============ HOST SURVEY ============
if survey_type == "host":
    st.subheader(f"📝 Your Meeting Notes: {contact_name}")
    if company:
        st.caption(f"🏢 {company}")
    st.caption(f"📅 Meeting Date: {meeting_date}")
    
    st.info("💡 Capture your thoughts while they're fresh! This saves directly to the CRM.")
    
    with st.form("host_survey", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            overall_rating = st.slider(
                "Overall meeting rating",
                min_value=1, max_value=5, value=4,
                help="1 = Poor, 5 = Excellent"
            )
        
        with col2:
            relationship_progress = st.selectbox(
                "Relationship progress",
                ["No connection", "Initial rapport", "Good connection", "Strong connection", "Partnership potential"],
                index=2
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            business_potential = st.selectbox(
                "Business/referral potential",
                ["None", "Low", "Medium", "High", "Immediate opportunity"],
                index=2
            )
        
        with col4:
            follow_up = st.selectbox(
                "Follow-up action",
                ["No follow-up needed", "Send info/proposal", "Schedule another meeting", "Make introduction", "Add to drip campaign"],
                index=0
            )
        
        key_takeaways = st.text_area(
            "🎯 Key takeaways",
            placeholder="What did you learn? What was discussed? Key insights?",
            height=120
        )
        
        action_items = st.text_area(
            "✅ Action items / Next steps",
            placeholder="What needs to happen next? Any promises made?",
            height=100
        )
        
        additional_notes = st.text_area(
            "📝 Additional notes",
            placeholder="Anything else worth remembering?",
            height=80
        )
        
        submitted = st.form_submit_button("💾 Save Meeting Notes", type="primary", use_container_width=True)
        
        if submitted:
            survey_result = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 HOST MEETING NOTES ({datetime.now().strftime('%Y-%m-%d %H:%M')})
Meeting Date: {meeting_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rating: {'⭐' * overall_rating} ({overall_rating}/5)
Relationship: {relationship_progress}
Business Potential: {business_potential}
Follow-up: {follow_up}

KEY TAKEAWAYS:
{key_takeaways.strip() if key_takeaways.strip() else '(none entered)'}

ACTION ITEMS:
{action_items.strip() if action_items.strip() else '(none entered)'}

NOTES:
{additional_notes.strip() if additional_notes.strip() else '(none entered)'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
            
            try:
                existing = supabase.table("contacts").select("notes").eq("id", contact_id).single().execute()
                existing_notes = existing.data.get("notes", "") or ""
                updated_notes = f"{existing_notes}\n\n{survey_result}" if existing_notes else survey_result
                
                supabase.table("contacts").update({
                    "notes": updated_notes,
                    "last_contacted": datetime.now().isoformat()
                }).eq("id", contact_id).execute()
                
                st.success("✅ Meeting notes saved to CRM!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error saving: {str(e)}")

# ============ ATTENDEE SURVEY ============
else:
    st.subheader("Thank you for meeting with Patrick!")
    st.caption(f"📅 Meeting Date: {meeting_date}")
    
    st.markdown("Your feedback helps us improve. **This takes less than 2 minutes.**")
    
    with st.form("attendee_survey", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            overall_rating = st.slider(
                "Meeting experience",
                min_value=1, max_value=5, value=4,
                help="1 = Poor, 5 = Excellent"
            )
        
        with col2:
            value_rating = st.slider(
                "Value of conversation",
                min_value=1, max_value=5, value=4,
                help="1 = Not valuable, 5 = Very valuable"
            )
        
        analysis_helpful = st.radio(
            "Was the Strategic Growth Analysis document helpful?",
            ["Very helpful", "Somewhat helpful", "Neutral", "Not very helpful", "Did not review it"],
            index=1,
            horizontal=True
        )
        
        topics_interest = st.multiselect(
            "Which services could benefit your business?",
            [
                "System Optimization",
                "Integration & Automation",
                "Custom Software Development",
                "AI Solutions",
                "CRM Implementation",
                "Marketing Automation",
                "Client Portal",
                "Technology & Systems Consulting",
                "None at this time"
            ]
        )
        
        follow_up_interest = st.radio(
            "Interested in a follow-up conversation?",
            ["Yes, definitely", "Maybe, send me more info", "Not at this time"],
            index=1,
            horizontal=True
        )
        
        open_feedback = st.text_area(
            "Any other feedback or suggestions?",
            placeholder="We genuinely appreciate your honest thoughts...",
            height=100
        )
        
        referral = st.text_input(
            "Know someone else who might benefit from meeting with Patrick?",
            placeholder="Name and contact info (optional)"
        )
        
        submitted = st.form_submit_button("📨 Submit Feedback", type="primary", use_container_width=True)
        
        if submitted:
            topics_str = ", ".join(topics_interest) if topics_interest else "None selected"
            survey_result = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ATTENDEE FEEDBACK ({datetime.now().strftime('%Y-%m-%d %H:%M')})
Meeting Date: {meeting_date}
From: {contact_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Experience: {'⭐' * overall_rating} ({overall_rating}/5)
Value: {'⭐' * value_rating} ({value_rating}/5)
Analysis Doc: {analysis_helpful}
Topics of Interest: {topics_str}
Follow-up Interest: {follow_up_interest}

FEEDBACK:
{open_feedback.strip() if open_feedback.strip() else '(none provided)'}

REFERRAL:
{referral.strip() if referral.strip() else '(none provided)'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
            
            try:
                existing = supabase.table("contacts").select("notes").eq("id", contact_id).single().execute()
                existing_notes = existing.data.get("notes", "") or ""
                updated_notes = f"{existing_notes}\n\n{survey_result}" if existing_notes else survey_result
                
                supabase.table("contacts").update({
                    "notes": updated_notes,
                    "last_contacted": datetime.now().isoformat()
                }).eq("id", contact_id).execute()
                
                st.success("✅ Thank you! Your feedback has been recorded.")
                st.balloons()
                
                st.markdown("---")
                st.markdown("**Learn more about Metro Point Technology:**")
                st.link_button("🌐 Visit Our Website", "https://metropointtech.com")
            except Exception as e:
                st.error(f"❌ Error saving: {str(e)}")

# Footer
st.markdown("---")
st.caption("Metro Point Technology LLC | (239) 600-8159 | support@metropointtech.com")
st.caption("Your feedback is confidential and used only to improve our services.")
