# Search Functionality Test Checklist

## Test Queries (5 searches)

1. **Company: Tesla**
   - ✅ Should show Tesla company card
   - ✅ Should display PP Rating
   - ✅ Should have image and description

2. **Sports: Mumbai Indians**
   - ✅ Should show Mumbai Indians team card
   - ✅ Should display PP Rating
   - ✅ Should have team badge/logo

3. **Movie: Inception**
   - ✅ Should show Inception movie card
   - ✅ Should display PP Rating
   - ✅ Should have poster and cast info

4. **Company: TATA**
   - ✅ Should show TATA company card
   - ✅ Should display PP Rating
   - ✅ Should have Wikipedia fallback if needed

5. **Sports: Chennai Super Kings**
   - ✅ Should show CSK team card
   - ✅ Should display PP Rating
   - ✅ Should have team information

## What to Check

### Backend (Server)
- [ ] Server is running on `http://localhost:5000`
- [ ] `/api/search/unified?query=Tesla` returns companies array
- [ ] `/api/search/unified?query=Mumbai Indians` returns sports array
- [ ] `/api/search/unified?query=Inception` returns movies array
- [ ] `/api/reviews/aggregate?query=Tesla` returns `public_pulse_rating`

### Frontend (Browser)
- [ ] Search bar accepts queries
- [ ] Entity cards appear below search bar
- [ ] Cards show title, image, description
- [ ] PP Rating displays (number or "N/A")
- [ ] Clicking rating navigates to entity page
- [ ] Related articles show below cards

### Console Checks
Open browser DevTools (F12) and check:
- [ ] No CORS errors
- [ ] `Unified search response:` shows correct data structure
- [ ] `UniversalSearchResults - Cards:` shows array of cards
- [ ] `UniversalSearchResults - Ratings:` shows rating object
- [ ] No `cardTitle.replace is not a function` errors

## Running the Test Script

```bash
# Make sure Flask server is running first
cd server
python run.py

# In another terminal, run the test
cd ..
python test_search_functionality.py
```

## Expected Results

Each search should:
1. Return entity cards (companies, sports, or movies)
2. Display PP Rating for each card
3. Show related articles below
4. Allow navigation to entity detail page

## Troubleshooting

### No Cards Showing
- Check browser console for errors
- Verify backend is running
- Check CORS configuration
- Verify Wikipedia fallback is working

### Ratings Not Showing
- Check `/api/reviews/aggregate` endpoint
- Verify API keys are valid (YouTube, Reddit, Twitter)
- Check browser console for rating fetch errors

### CORS Errors
- Verify CORS is configured in `server/app/__init__.py`
- Check that frontend is on `localhost:3000`
- Restart Flask server after CORS changes

