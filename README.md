# AeroBMSCE recruitment task concept

A responsive, static redesign concept for the AeroBMSCE web development recruitment task. This is not the official club website. It has no backend or message-submission form; the contact link opens the source-listed email address in the visitor's mail application.

## Audit inventory and implementation plan

- **Useful source content:** club background and vision, named student teams, aircraft/UAV and research directions, competition milestones, proposed partner tiers, and the listed contact email/location.
- **Provided assets:** club logos, aircraft and competition photos (`photo1.jpg`–`photo7.jpg`), partner-tier icons, organization/tool logos, and a CAD aircraft illustration. The original home page referenced `photo8.jpg`, which is not in the supplied folder.
- **Plan:** retain source-backed material and imagery in one responsive static page with six section destinations; provide accessible shared navigation and a contact action; keep the legacy journey, partner, about, and contact URLs usable through relative redirects; avoid a build step so the root entry file can deploy directly to GitHub Pages.

## 1. What were the most noticeable flaws in the original website?

The supplied pages use a fixed 1,480px content width, small low-contrast serif body text, a maroon header and inconsistent navigation. Images have fixed dimensions and do not adapt cleanly to smaller screens. Keyboard focus outlines are disabled. The home-page Contact link points to a missing `contact.html` (verified as a live 404); the live `about.html` path also returns 404. The partner page opens with competition copy rather than partnership information. The journey content contains conflicting club-history statistics and current-season competition entries without clear verification status.

## 2. What was the design route, and what UI/UX decisions were made?

The redesign takes an editorial aerospace direction: a deep navy hero and header, warm off-white reading surfaces, restrained gold accents inspired by the provided club logo, large typography, and real team/UAV photography from `images/`. It reuses the source partner-tier icons and organization/tool marks while clearly identifying those marks as unconfirmed source references. The home page uses one continuous layout for Who We Are, What We Build, Achievements, Partner With Us, and Contact. Navigation and calls to action use real section anchors; the logo links home; the mobile menu exposes its expanded state, closes on selection or Escape, and provides visible keyboard focus. Images use responsive crops and descriptive alt text; reduced-motion preferences are respected. Existing `journey.html`, `partners.html`, `about.html`, and `contact.html` routes redirect with relative links to their corresponding sections. No social links or form were invented.

## 3. Describe one problem or edge case encountered, how it appeared, and the steps taken to work around it.

The original home page referenced `images/photo8.jpg` for its banner, but that file is not present in the supplied image folder (the supplied set ends at `photo7.jpg`). This left a broken hero asset. I replaced it with the supplied aircraft/team photo at `images/photo2.jpg` and built the hero treatment around that real asset. All image paths and legacy-page redirects are relative so they work beneath the GitHub Pages project path.

## Content to verify before official publication

- The starter's home page says AeroBMSCE was established in 2012, while the journey page also says “16+ years.” These conflict for a 2026 site. The conflicting duration is omitted.
- The journey page claims 75+ projects, 50+ research papers/reports/certifications, and 20+ podium finishes. These aggregate claims are omitted pending confirmation.
- The journey source lists 2026 SAE International Aero Design West and SAE Aerothon results. They are marked as source-listed in the site and need current-season verification.
- The source's upcoming competition and research project lists may be stale. Confirm dates and current project status before representing any as active.
- Partner tiers and example benefits are proposals listed in the source, not confirmed agreements. Confirm scope, availability, and partner relationships before making promises.
- The source lists `aerobmsce@bmsce.ac.in` and Propel Lab–3. Confirm the email and location remain current.

## GitHub Pages deployment

This is a plain static site. `index.html` is at the repository root; no build step or dependency installation is required.

1. From a clone of your fork, commit the changes and push the working branch:

   ```powershell
   git add .
   git commit -m "Redesign AeroBMSCE recruitment website"
   git push -u origin sindhugowda1118-code-aerobmsce-site-redesign
   ```

2. In the fork on GitHub, open **Settings → Pages**. Select **Deploy from a branch**, choose `sindhugowda1118-code-aerobmsce-site-redesign` and `/(root)`, then save. Alternatively, merge the branch into `main` first and select `main` / `/(root)`.
3. Wait for the Pages deployment to finish. The project URL is typically `https://<owner>.github.io/AeroBMSCE_TASK_REPO/`. Verify the home page, all six section links (`#home`, `#who-we-are`, `#what-we-build`, `#achievements`, `#partners`, and `#contact`), the mobile menu, and the legacy `journey.html` and `partners.html` redirects. Check image loading on the project URL (not only at `/`).
4. Copy the public fork repository URL and the verified live Pages URL into the AeroBMSCE recruitment task's Google Form. The form has not been submitted on your behalf.
