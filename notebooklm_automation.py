import asyncio
import threading
from notebooklm import NotebookLMClient


def normalize(s: str) -> str:
    return s.lower().replace("_", " ").replace("-", " ").strip()


async def _add_to_notebooklm(notebook_title: str, video_urls: list[str], logs: list) -> str:
    logs.append("Connecting to NotebookLM...")
    async with await NotebookLMClient.from_storage() as client:

        existing_notebooks = await client.notebooks.list()
        notebook = next(
            (nb for nb in existing_notebooks if normalize(nb.title) == normalize(notebook_title)),
            None
        )

        if notebook:
            logs.append(f"Found existing notebook '{notebook.title}' — syncing sources...")
        else:
            logs.append(f"Creating new notebook '{notebook_title}'...")
            notebook = await client.notebooks.create(title=notebook_title)
            logs.append(f"Notebook created (id: {notebook.id})")

        existing_sources = await client.sources.list(notebook_id=notebook.id)
        existing_titles = {s.title for s in existing_sources if s.title}
        logs.append(f"Notebook has {len(existing_titles)} existing sources.")

        added = 0
        failed = 0
        for i, url in enumerate(video_urls, 1):
            try:
                source = await client.sources.add_url(notebook_id=notebook.id, url=url)
                if source.title in existing_titles:
                    await client.sources.delete(notebook_id=notebook.id, source_id=source.id)
                else:
                    existing_titles.add(source.title)
                    logs.append(f"Added {i}/{len(video_urls)}: {source.title}")
                    added += 1
            except Exception as e:
                err = str(e).lower()
                if "duplicate" in err or "already" in err or "exists" in err:
                    pass
                else:
                    logs.append(f"Could not add {url}: {e}")
                    failed += 1

        logs.append(f"Done! {added} new sources added.")
        if failed:
            logs.append(f"{failed} URLs could not be added (unavailable/private videos).")

        notebook_url = f"https://notebooklm.google.com/notebook/{notebook.id}"
        logs.append(f"Notebook URL: {notebook_url}")
        return notebook_url


async def _query_notebook(notebook_id: str, query: str, logs: list) -> str:
    logs.append(f"Running query: {query}")
    async with await NotebookLMClient.from_storage() as client:
        response = await client.chat.ask(notebook_id=notebook_id, question=query)
        answer = getattr(response, "answer", None) or getattr(response, "text", None) or str(response)
        logs.append("Query complete.")
        return answer


def query_notebooklm(notebook_id: str, query: str) -> tuple[str, list[str]]:
    logs = []
    result = {"answer": "", "error": None}

    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result["answer"] = loop.run_until_complete(_query_notebook(notebook_id, query, logs))
        except Exception as e:
            result["error"] = e
            logs.append(f"Query error: {e}")
        finally:
            loop.close()

    t = threading.Thread(target=run)
    t.start()
    t.join()

    if result["error"]:
        raise result["error"]
    return result["answer"], logs


def run_notebooklm(notebook_title: str, video_urls: list[str]) -> tuple[str, list[str]]:
    logs = []
    result = {"url": "", "error": None}

    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result["url"] = loop.run_until_complete(
                _add_to_notebooklm(notebook_title, video_urls, logs)
            )
        except Exception as e:
            result["error"] = e
            logs.append(f"Error: {e}")
        finally:
            loop.close()

    t = threading.Thread(target=run)
    t.start()
    t.join()

    if result["error"]:
        raise result["error"]
    return result["url"], logs
