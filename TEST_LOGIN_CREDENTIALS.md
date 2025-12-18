# Test Login Credentials

All test users can log in using the login page at: **`/accounts/login/`**

## Default Password
**All test accounts use the same password:**
```
testpass123
```

---

## Volunteer Accounts

### 1. Aisha Khan
- **Username**: `aisha.khan`
- **Email**: `aisha.khan@student.ncl.ac.uk`
- **Password**: `testpass123`
- **Role**: Volunteer
- **Course**: Computer Science
- **After login**: Redirects to Volunteer Dashboard

### 2. Tom Reynolds
- **Username**: `tom.reynolds`
- **Email**: `tom.reynolds@student.ncl.ac.uk`
- **Password**: `testpass123`
- **Role**: Volunteer
- **Course**: Business & Marketing
- **After login**: Redirects to Volunteer Dashboard

### 3. Mei Lin
- **Username**: `mei.lin`
- **Email**: `mei.lin@student.ncl.ac.uk`
- **Password**: `testpass123`
- **Role**: Volunteer
- **Course**: Biomedical Science
- **After login**: Redirects to Volunteer Dashboard

---

## Organisation Admin Accounts

### 1. North East Food Support Network
- **Username**: `nefoodsupport_admin`
- **Email**: `contact@nefoodsupport.org`
- **Password**: `testpass123`
- **Role**: Organisation Admin
- **Name**: Sarah Mitchell
- **After login**: Redirects to Organisation Dashboard

### 2. GreenSteps Environmental Collective
- **Username**: `greensteps_admin`
- **Email**: `info@greensteps.org.uk`
- **Password**: `testpass123`
- **Role**: Organisation Admin
- **Name**: James Anderson
- **After login**: Redirects to Organisation Dashboard

### 3. CodeForward Youth Mentoring
- **Username**: `codeforward_admin`
- **Email**: `hello@codeforward.org`
- **Password**: `testpass123`
- **Role**: Organisation Admin
- **Name**: David Thompson
- **After login**: Redirects to Organisation Dashboard

### 4. BrightMind Wellbeing Hub
- **Username**: `brightmind_admin`
- **Email**: `support@brightmind.org.uk`
- **Password**: `testpass123`
- **Role**: Organisation Admin
- **Name**: Emma Wilson
- **After login**: Redirects to Organisation Dashboard

### 5. Heritage Hands Community Museum
- **Username**: `heritagehands_admin`
- **Email**: `info@heritagehands.org`
- **Password**: `testpass123`
- **Role**: Organisation Admin
- **Name**: Robert Brown
- **After login**: Redirects to Organisation Dashboard

---

## How to Login

1. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Navigate to the login page:**
   - URL: `http://localhost:8000/accounts/login/`
   - Or click "Login" from the landing page

3. **Enter credentials:**
   - Username: (use any username from above)
   - Password: `testpass123`

4. **After login:**
   - **Volunteers** → Redirected to `/volunteers/dashboard/`
   - **Organisation Admins** → Redirected to `/organisations/dashboard/`

---

## Quick Test Scenarios

### Test Volunteer Features
- Login as `aisha.khan` to test volunteer dashboard
- Browse opportunities
- View recommended opportunities (matching algorithm)
- Apply to opportunities
- View applications

### Test Organisation Features
- Login as `nefoodsupport_admin` to test organisation dashboard
- View posted opportunities
- View applications from volunteers
- Accept/reject applications
- Manage opportunities

### Test Matching Algorithm
- Login as `aisha.khan` (Computer Science student)
  - Should see high matches for coding/tech opportunities
  - Should see low matches for park clean-up
  
- Login as `tom.reynolds` (Marketing student, prefers remote)
  - Should see high matches for remote content creation roles
  - Should see lower matches for onsite physical work

- Login as `mei.lin` (Biomedical Science, max 4 hrs/week)
  - Should see healthcare opportunities ranked high
  - Should NOT see 4+ hour opportunities if already committed

---

## Notes

- All accounts are fully functional and ready for testing
- All organisations are auto-verified (verified=True)
- All opportunities are set to OPEN status
- Volunteer profiles are complete with skills, interests, and availability
- Passwords are intentionally simple for testing purposes
- In production, these should be changed to secure passwords

---

## URL Routes

- **Login**: `/accounts/login/`
- **Logout**: `/accounts/logout/`
- **Register**: `/accounts/register/`
- **Volunteer Dashboard**: `/volunteers/dashboard/`
- **Organisation Dashboard**: `/organisations/dashboard/`
- **Browse Opportunities**: `/opportunities/browse/`

