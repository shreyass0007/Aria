# Notion Integration Setup

To enable Aria to interact with your Notion workspace, you need to provide an API Key and a Database ID.

## 1. Get Notion API Key
1. Go to [Notion My Integrations](https://www.notion.so/my-integrations).
2. Click **New integration**.
3. Name it "Aria" and select the workspace you want to use.
4. Click **Submit**.
5. Copy the **Internal Integration Secret** (this is your `NOTION_API_KEY`).

## 2. Get Database ID
1. Open the Notion database (page) you want to use (e.g., a Task list or Notes database).
2. Click the `...` menu at the top right of the page.
3. Click **Copy link**.
4. The link will look like this: `https://www.notion.so/username/1234567890abcdef1234567890abcdef?v=...`
5. The part between the last `/` and the `?` is your **Database ID** (`1234567890abcdef1234567890abcdef`).

## 3. Connect Integration to Database
1. Go to the database page in Notion.
2. Click the `...` menu at the top right.
3. Click **Connect to** (or **Add connections**).
4. Search for "Aria" (the integration you created) and select it.
5. Confirm the connection.

## 4. Update .env File
Add the following lines to your `.env` file:

```env
NOTION_API_KEY=your_secret_key_here
NOTION_DATABASE_ID=your_database_id_here
```
