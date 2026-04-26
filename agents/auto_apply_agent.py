# agents/auto_apply_agent.py
from playwright.sync_api import sync_playwright
import time
import os

class AutoApplyAgent:
    @staticmethod
    def attempt_apply(job_url, parsed_resume, resume_pdf_path):
        """
        Attempts to fill out a job application form using heuristic selectors.
        Returns (success_bool, status_message, screenshot_path)
        """
        screenshot_path = "data/last_apply_attempt.png"
        
        # Ensure we have a place to save the screenshot
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)  # Launch visibly so user can see it
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # Setup timeout so it doesn't hang forever
                page.set_default_timeout(15000)

                # 1. Navigate to the job URL
                try:
                    page.goto(job_url, wait_until="networkidle")
                except Exception as e:
                    page.screenshot(path=screenshot_path)
                    return False, f"Failed to load page: {str(e)}", screenshot_path

                time.sleep(2) # Give dynamic JS time to render

                # Extract basic info safely
                personal_info = parsed_resume.get("personal_information", {})
                contact_info = parsed_resume.get("contact_info", {})
                
                name = personal_info.get("name", "")
                if not name:
                    name = contact_info.get("name", "") # Fallback

                email = contact_info.get("email", "")
                phone = contact_info.get("phone", "")
                linkedin = contact_info.get("linkedin", "")

                # 2. Heuristic Form Filling
                # We try to find inputs by their 'name', 'id', 'aria-label', or placeholder
                
                # First Name / Full Name
                if name:
                    try:
                        # Try finding something with name, full name, first name
                        name_input = page.locator("input[name*='name' i], input[id*='name' i], input[placeholder*='name' i]").first
                        if name_input.is_visible():
                            name_input.fill(name)
                    except Exception:
                        pass
                
                # Email
                if email:
                    try:
                        email_input = page.locator("input[type='email'], input[name*='email' i], input[id*='email' i]").first
                        if email_input.is_visible():
                            email_input.fill(email)
                    except Exception:
                        pass

                # Phone
                if phone:
                    try:
                        phone_input = page.locator("input[type='tel'], input[name*='phone' i], input[id*='phone' i]").first
                        if phone_input.is_visible():
                            phone_input.fill(phone)
                    except Exception:
                        pass

                # LinkedIn / Portfolio URL
                if linkedin:
                    try:
                        linkedin_input = page.locator("input[name*='linkedin' i], input[name*='url' i], input[placeholder*='linkedin' i]").first
                        if linkedin_input.is_visible():
                            linkedin_input.fill(linkedin)
                    except Exception:
                        pass

                # 3. Upload Resume PDF
                if os.path.exists(resume_pdf_path):
                    try:
                        # Find any generic file upload input
                        file_input = page.locator("input[type='file']").first
                        if file_input.is_visible() or file_input.is_hidden(): # File inputs are often hidden behind styled buttons
                            file_input.set_input_files(resume_pdf_path)
                    except Exception:
                        pass
                
                # We purposely DO NOT click submit automatically. 
                # This is a beta feature and we want the user to review the application and solve CAPTCHAs.
                
                # Wait for 5 seconds so the user can see what got filled
                time.sleep(5)
                
                page.screenshot(path=screenshot_path)
                browser.close()
                
                return True, "Form fields filled. Review browser screenshot. You may need to click submit or resolve CAPTCHAs manually.", screenshot_path

        except Exception as e:
            return False, f"Playwright error: {str(e)}", screenshot_path
