---
name: people-search-scrub
description: Remove the user's phone number and listings from people-search sites and data brokers: reverse-search the number per site, submit the official opt-out, finish email confirmations from the user's inbox, and report per site. Use when the user asks for a privacy scrub or a re-check.
---

# People-search scrub

Owner details (minimum only). The installing Muse fills these in by asking
the user once, and keeps the answers in the user's own memory or private
notes, never in a shared copy of this skill:
- Name: <FULL_NAME>
- Phone to remove: <PHONE_NUMBER>
- City/state: <CITY>, <STATE> (brokers may list other towns from address history; a reverse phone search surfaces whatever exists)
- Confirmation email: <EMAIL> (if Muse can read this inbox, it can finish confirmation links)
- Date of birth: ask the user only if a site requires it (PeopleConnect does, and it cannot be changed once entered). Never guess when sites disagree.
- Never ask for or enter IDs, passwords, or payment.

## Steps

1. One browser task at a time. For each site: reverse-search the phone number; if listed, open the site's official opt-out page and submit. Skip sites showing nothing. Attempt captchas; stop at sign-in, password, payment, or ID prompts and report the block.
2. Sites in order:
   - TruePeopleSearch — truepeoplesearch.com/removal
   - FastPeopleSearch — fastpeoplesearch.com/optout
   - That's Them — thatsthem.com/optout
   - Spokeo — spokeo.com/optout (needs the profile URL)
   - Whitepages — whitepages.com/suppression-requests (needs the /name/... profile URL and an automated phone call the user must answer personally; hand them the URL and steps)
   - BeenVerified — beenverified.com/app/optout/search (its captcha may fail from an automated browser; then the user submits it or a real-profile session is used)
   - MyLife — mylife.com/privacyrequest
   - PeopleConnect suppression center — suppression.peopleconnect.us (covers Intelius, US Search, ZabaSearch, Addresses.com; email verification link expires in 15 minutes, plus date of birth and an SMS code to the user's phone)
   - PeopleFinders — peoplefinders.com/opt-out
   - Nuwber — nuwber.com
   - Radaris — radaris.com (check whether it still operates)
3. Many sites send a confirmation email as step 1. Read the user's email, then pass the exact links to the browser task. Time-limited links (PeopleConnect, 15 minutes) go first.
4. For phone codes, ask the user to paste the code, then enter it in a fresh browser task.
5. Anything only the user can do (the Whitepages call, clicking links in their own inbox, registering at donotcall.gov): give them the exact URL and what to enter.

## Finish

Report per site: submitted, pending confirmation, blocked (with reason), or not listed. Remind him to register at donotcall.gov himself. Brokers repopulate, so ask how often he wants automatic re-checks (weekly, every two weeks, monthly, quarterly, or never) and schedule accordingly.

## Rules

Only act for the person who asked you. Report only what pages actually said.
