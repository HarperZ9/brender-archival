from __future__ import annotations


def json_receipt_helpers_source() -> str:
    """C helpers for JSON receipts emitted by generated smoke programs."""
    return r"""

static void json_write_string(FILE *out, const char *value)
{
    const unsigned char *p;
    fputc('"', out);
    if (value != NULL) {
        for (p = (const unsigned char *)value; *p != '\0'; p++) {
            unsigned char ch = *p;
            switch (ch) {
            case '"': fputs("\\\"", out); break;
            case '\\': fputs("\\\\", out); break;
            case '\b': fputs("\\b", out); break;
            case '\f': fputs("\\f", out); break;
            case '\n': fputs("\\n", out); break;
            case '\r': fputs("\\r", out); break;
            case '\t': fputs("\\t", out); break;
            default:
                if (ch < 0x20) {
                    fprintf(out, "\\u%04x", (unsigned int)ch);
                } else {
                    fputc(ch, out);
                }
                break;
            }
        }
    }
    fputc('"', out);
}
"""
