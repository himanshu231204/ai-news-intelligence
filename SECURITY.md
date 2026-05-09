# 🔒 Security Policy

## Reporting Security Vulnerabilities

We take security vulnerabilities seriously. If you discover a security issue,
please report it responsibly.

### How to Report

1. **DO NOT** create a public GitHub issue
2. **Email** the maintainers directly: security@example.com
3. **Include** in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 24 hours
- **Initial assessment**: Within 7 days
- **Fix timeline**: Based on severity (see below)

| Severity | Response Time | Fix Time |
|----------|---------------|----------|
| Critical | 24 hours | 7 days |
| High | 48 hours | 14 days |
| Medium | 7 days | 30 days |
| Low | 14 days | Next release |

---

## Security Best Practices

### API Keys

- **Never commit** API keys to version control
- **Use environment variables** for all secrets
- **Rotate keys** regularly
- **Use least privilege** - Only grant necessary permissions

### Environment Configuration

```env
# ✅ Good - Using environment variables
GROQ_API_KEY=${GROQ_API_KEY}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}

# ❌ Bad - Hardcoded keys
GROQ_API_KEY=gsk_123456789
```

### Rate Limiting

- Respect API rate limits
- Implement exponential backoff
- Cache responses when possible

### Data Handling

- Validate all user inputs
- Sanitize data before processing
- Store sensitive data encrypted

---

## Supported Versions

| Version | Supported | Notes |
|---------|-----------|-------|
| Latest | ✅ | Active development |
| v1.x | ✅ | Security updates |
| v0.x | ❌ | End of life |

---

## Security Checklist

Before deploying to production:

- [ ] All API keys are environment variables
- [ ] No secrets in configuration files
- [ ] Database connections are encrypted
- [ ] HTTPS enabled for all endpoints
- [ ] Rate limiting configured
- [ ] Logging configured (no sensitive data)
- [ ] Error messages don't leak sensitive info

---

## Third-Party Dependencies

We regularly update dependencies to patch security vulnerabilities.

```bash
# Check for vulnerabilities
pip audit

# Update dependencies safely
pip install -r requirements.txt --upgrade
```

---

## Security Updates

Security updates will be released as:

- **Hotfix** - Critical vulnerabilities
- **Minor releases** - Medium/low severity
- **Security advisory** - Published on GitHub

---

## Contact

For security-related inquiries:
- Email: security@example.com
- GitHub: [Security Advisories](https://github.com/yourusername/ai-news-agent/security/advisories)

---

*Thank you for helping keep this project secure!*