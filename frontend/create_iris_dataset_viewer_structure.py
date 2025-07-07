import os

structure = {
    "": [
        ".env.example",
        "package.json",
        "tsconfig.json",
        "tailwind.config.ts",
        "next.config.js"
    ],
    "public": [],
    "src/app/api/login": ["route.ts"],
    "src/app/api/logout": ["route.ts"],
    "src/app/api/data": ["route.ts"],
    "src/app/api/check-auth": ["route.ts"],
    "src/app": [
        "layout.tsx",
        "page.tsx",
        "globals.css"
    ],
    "src/components": [
        "Login.tsx",
        "Dashboard.tsx"
    ],
    "src/lib": [
        "auth.ts",
        "data.ts",
        "session.ts"
    ],
    "src/types": [
        "index.ts"
    ]
}

def create_structure(base="iris-dataset-viewer"):
    for folder, files in structure.items():
        for filename in files:
            file_path = os.path.join(base, folder, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                ext = os.path.splitext(filename)[-1]
                comment = (
                    f"// {filename} placeholder\n" if ext in [".ts", ".tsx", ".js", ".json"] else
                    f"/* {filename} placeholder */\n" if ext == ".css" else
                    f"# {filename} placeholder\n" if ext == ".env" else
                    ""
                )
                f.write(comment)
    print(f"✅ Structure created in ./{base}/")

if __name__ == "__main__":
    create_structure()
