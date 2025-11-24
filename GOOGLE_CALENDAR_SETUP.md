# 🗓️ Google Calendar Setup Guide for Aria

This guide will help you enable Google Calendar integration for Aria so you can schedule meetings and check your events using voice commands.

## Prerequisites
- A Google Account (Gmail)
- Aria installed on your system

---

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project dropdown at the top left (next to the Google Cloud logo).
3. Click **New Project**.
4. Name it `Aria-Assistant` (or anything you like) and click **Create**.
5. Select your new project from the notification bell or the project dropdown.

## Step 2: Enable Google Calendar API

1. In the left sidebar, go to **APIs & Services** > **Library**.
2. Search for **"Google Calendar API"**.
3. Click on **Google Calendar API** and then click **Enable**.

## Step 3: Configure OAuth Consent Screen

1. In the left sidebar, go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** user type and click **Create**.
3. **App Information**:
   - **App name**: Aria
   - **User support email**: Select your email.
   - **Developer contact information**: Enter your email.
   - Click **Save and Continue**.
4. **Scopes**:
   - Click **Add or Remove Scopes**.
   - Search for `calendar` and select `.../auth/calendar` (See, edit, share, and permanently delete all the calendars you can access using Google Calendar).
   - Click **Update**, then **Save and Continue**.
5. **Test Users**:
   - Click **+ ADD USERS**.
   - Enter your own email address (e.g., `yourname@gmail.com`).
   - Click **Add**, then **Save and Continue**.
   - **Important**: If you don't add yourself as a test user, you will get an "Access Blocked" error.

## Step 4: Create Credentials

1. In the left sidebar, go to **APIs & Services** > **Credentials**.
2. Click **+ CREATE CREDENTIALS** at the top and select **OAuth client ID**.
3. **Application type**: Select **Desktop app**.
4. **Name**: `Aria Desktop` (or leave default).
5. Click **Create**.
6. A popup will appear. Click **Download JSON** (the download icon).
7. Rename the downloaded file to `credentials.json`.

## Step 5: Install Credentials

1. Move the `credentials.json` file into your Aria project folder:
   ```
   d:\CODEING\PROJECTS\ARIA\credentials.json
   ```

## Step 6: First Run & Authentication

1. Start Aria (or run the test script).
2. A browser window will open asking you to sign in.
3. Select your account.
4. You may see a warning "Google hasn't verified this app". Click **Continue** or **Advanced > Go to Aria (unsafe)**.
5. Click **Allow** to grant permissions.
6. You will see "The authentication flow has completed". You can close the browser.

🎉 **Success!** Aria is now connected to your Google Calendar.

---

## Troubleshooting

### "Access blocked: aria has not completed the Google verification process"
- **Cause**: You didn't add your email to the "Test Users" list.
- **Fix**: Go back to Step 3 (Test Users) and add your email address.

### "Token has been expired or revoked"
- **Fix**: Delete the `token.pickle` file in your project folder and restart Aria to re-authenticate.

### "Calendar service not available"
- **Fix**: Ensure `credentials.json` is in the correct folder and is a valid JSON file.
