# Volink - Intelligent Volunteer Matching Platform

Volink is a web-based volunteering platform designed for university contexts, connecting students with meaningful volunteering opportunities through intelligent skill based matching.

## Features

- **Smart Matching Engine**: Matches volunteers to opportunities based on skills, interests, availability, and workload
- **Opportunity Management**: Organisations can create and manage volunteering opportunities
- **Application Workflow**: Complete application lifecycle with status tracking and notifications
- **Schedule Management**: Prevents over-commitment by tracking hours and availability
- **Participation Tracking**: Log and track volunteer hours with detailed analytics
- **Role-Based Access**: Separate interfaces for volunteers and organisation administrators

## Technology Stack

- **Backend**: Django 5.x (Python)
- **Database**: PostgreSQL
- **Frontend**: Django Templates with Tailwind CSS (CDN)
- **JavaScript**: Vanilla JavaScript (no frameworks)
- **Testing**: pytest-django

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip

### Installation

1. Clone the repository:
```bash
cd Volink
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

5. Set up the database:
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Testing

Run all tests:
```bash
python manage.py test
```

Run specific test files:
```bash
python manage.py test tests.test_matching
python manage.py test tests.test_scheduling
python manage.py test tests.test_models
python manage.py test tests.test_workflows
```

## Project Structure

```
Volink/
├── accounts/          # User management and authentication
├── organisations/     # Organisation management
├── opportunities/     # Opportunity and application management
├── volunteers/        # Volunteer features (matching, scheduling, participation)
├── notifications/    # Notification system
├── templates/        # Base templates
├── tests/            # Test files
└── volink/           # Django project settings
```

## Documentation

See the `docs/` folder for detailed documentation:
- `epic.md` - Project epic and overview
- `user_stories.md` - User stories
- `story_mapping.md` - User journey mapping
- `features_plan.md` - Feature breakdown and story splitting
- `qa_plan.md` - Quality assurance plan
- `competitor_analysis.md` - Competitor analysis and USP
- `implemented_vs_simulated.md` - Feature implementation status

## Wizard of Oz Features

Some features are simulated for demonstration:
- **Email Notifications**: Logged to console instead of sending emails
- **Advanced Analytics**: Hardcoded example charts and visualizations
- **External Integrations**: Calendar and social media integrations are placeholders

All simulated features are clearly marked in the UI with banners.

 
