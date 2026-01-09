# Authentication Guide

The TraceID Log Service is protected with API Key authentication to ensure only authorized users can access Splunk logs.

---

## 🔐 How It Works

1. **Login Page:** Users are presented with a login page when they first visit the application
2. **API Key Entry:** Users must enter a valid API key to access the service
3. **Session Storage:** The API key is stored in the browser's localStorage for the session
4. **Request Authentication:** All API requests include the API key in the `X-API-Key` header
5. **Logout:** Users can logout, which clears the API key from localStorage

---

## 🔑 Generating an API Key

### Option 1: Using Python (Recommended)

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output:
```
xK8vN2Qp9wR5tM3hF7jL4sD6aZ1bY0cG8eT5oU2iP4q
```

### Option 2: Using OpenSSL

```bash
openssl rand -base64 32
```

### Option 3: Online Generator

Use a secure password generator like:
- https://www.lastpass.com/features/password-generator
- Minimum 32 characters
- Include letters, numbers, and special characters

---

## 🚀 Setting Up Authentication

### For Local Development

1. **Generate API Key:**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Add to `.env` file:**
   ```bash
   cp env.example .env
   nano .env
   ```

3. **Set the API_KEY:**
   ```env
   API_KEY=your-generated-api-key-here
   ```

4. **Start the application:**
   ```bash
   uv run python main.py
   ```

5. **Open browser and login:**
   - Go to http://localhost:8002
   - Enter your API key
   - Start searching logs!

---

### For Render Deployment

1. **Generate API Key** (as shown above)

2. **Set in Render Dashboard:**
   - Go to your service in Render
   - Navigate to **Environment** tab
   - Click **"Add Environment Variable"**
   - Key: `API_KEY`
   - Value: Your generated API key
   - Click **"Save Changes"**

3. **Share with Users:**
   - Send the API key to authorized users via **secure channel** (not email!)
   - Use encrypted messaging (Signal, WhatsApp, Slack DM, etc.)
   - Or use a password manager to share securely

4. **Users Login:**
   - Users visit your Render URL
   - Enter the API key you shared
   - Start searching!

---

## 👥 Sharing API Key with Customers

### ✅ Secure Methods:

1. **Encrypted Messaging:**
   - Signal
   - WhatsApp
   - Slack DM
   - Microsoft Teams

2. **Password Managers:**
   - 1Password (secure sharing)
   - LastPass
   - Bitwarden

3. **Secrets Management:**
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault

### ❌ Insecure Methods (Avoid):

- ❌ Plain email
- ❌ Unencrypted chat
- ❌ Text message (SMS)
- ❌ Shared documents
- ❌ Slack public channels

---

## 🔄 Rotating API Keys

It's good practice to rotate API keys periodically (e.g., every 90 days).

### Steps to Rotate:

1. **Generate new API key:**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update on Render:**
   - Go to Environment tab
   - Update `API_KEY` value
   - Service will auto-restart

3. **Notify users:**
   - Inform all users of the new key
   - Share via secure channel
   - Set a deadline for switching

4. **Old key stops working immediately** after service restarts

---

## 🛡️ Security Best Practices

### For Administrators:

1. ✅ **Strong Keys:** Always use cryptographically secure random keys (32+ characters)
2. ✅ **Secrets Management:** Store in environment variables, never in code
3. ✅ **Regular Rotation:** Rotate keys every 3-6 months
4. ✅ **Access Control:** Only share with authorized users
5. ✅ **Monitoring:** Check application logs for authentication failures
6. ✅ **HTTPS:** Always use HTTPS in production (Render provides this automatically)

### For Users:

1. ✅ **Keep It Secret:** Never share your API key publicly
2. ✅ **Secure Storage:** Use a password manager
3. ✅ **Logout:** Click logout when done on shared computers
4. ✅ **Report Compromise:** Notify admin immediately if key is exposed

---

## 🔍 Monitoring Access

### Check Application Logs

In Render dashboard, go to **Logs** tab to see:

```
INFO - Searching logs for traceId=abc-123-def, aem_service=...
WARNING - Missing API key for request to /api/logs/search
WARNING - Invalid API key attempted for /api/logs/search
```

**Suspicious Activity:**
- Multiple failed authentication attempts
- Requests from unexpected IP addresses
- Unusual search patterns

**Action:** Rotate API key immediately if suspicious activity detected.

---

## 🆘 Troubleshooting

### "Missing API Key" Error

**Cause:** API key not sent with request

**Solution:**
1. Make sure you're logged in
2. Check browser localStorage: `localStorage.getItem('apiKey')`
3. Clear browser cache and login again

### "Invalid API Key" Error

**Cause:** Wrong API key or key has been rotated

**Solution:**
1. Verify you have the correct API key
2. Contact administrator for current key
3. Logout and login with new key

### Service Won't Start

**Cause:** `API_KEY` environment variable not set

**Solution:**
1. Check Render dashboard → Environment tab
2. Ensure `API_KEY` is set
3. Restart service if needed

---

## 🎯 Quick Reference

| Task | Command/Action |
|------|----------------|
| Generate API Key | `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |
| Set Locally | Add to `.env` file: `API_KEY=your-key` |
| Set on Render | Dashboard → Environment → Add `API_KEY` |
| Share Securely | Use encrypted messaging or password manager |
| Rotate Key | Generate new → Update on Render → Notify users |
| Check Logs | Render Dashboard → Logs tab |

---

## 📧 Support

If you have questions about authentication:
1. Check this guide first
2. Review application logs
3. Contact your system administrator

---

**Remember:** The API key is the only barrier between the public internet and your Splunk data. Keep it secure! 🔒

