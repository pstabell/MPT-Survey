# MPT Survey

Public post-meeting survey app for Metro Point Technology.

## Features

- **Attendee Survey**: Collects feedback from meeting attendees
- **Host Survey**: Patrick's self-assessment and meeting notes
- **CRM Integration**: Results automatically saved to contact notes in MPT-CRM

## Usage

Survey links are generated with query parameters:
```
https://mpt-survey.streamlit.app/?contact_id=xxx&type=attendee&date=2026-02-17
https://mpt-survey.streamlit.app/?contact_id=xxx&type=host&date=2026-02-17
```

## Deployment

Deployed on Streamlit Community Cloud. Secrets configured in Streamlit dashboard.

## Related

- MPT-CRM: Main CRM application
- Meeting Lifecycle Automation: Generates survey emails automatically
