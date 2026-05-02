
            st.error(f"⚠️ Google Sign-In setup error: {_oauth_error}")

        if _google_url:
            # Use components.html with window.top.location.href for same-tab navigation
            # Render as <a target="_top"> — anchor navigation works from sandboxed iframes
            # where window.top.location.href is blocked by the browser's security policy.
            import streamlit.components.v1 as _components
            _components.html(f"""
            <!DOCTYPE html>
                font-size:15px; font-weight:600; width:100%;
                box-shadow:0 2px 8px rgba(0,0,0,0.10);
                transition:all .18s ease;
                text-decoration:none;
            }}
            .gbtn:hover {{ box-shadow:0 4px 16px rgba(0,0,0,0.18); border-color:#B0B8C4; background:#FAFAFA; }}
            </style>
            </head>
            <body>
            <button class="gbtn" id="gbtn">
            <a class="gbtn" href="{_google_url}" target="_top">
                <svg width="20" height="20" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.34-8.16 2.34-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>
                Continue with Google
            </button>
            <script>
            document.getElementById('gbtn').addEventListener('click', function() {{
                window.top.location.href = '{_google_url}';
            }});
            </script>
            </a>
            </body>
            </html>
            """, height=58, scrolling=False)
