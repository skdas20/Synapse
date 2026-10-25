"""Structural checks for the FastAPI route declarations."""

import ast
from pathlib import Path
import unittest


APP_PATH = Path(__file__).resolve().parents[1] / "backend" / "app.py"
API_DOC_PATH = Path(__file__).resolve().parents[1] / "docs" / "API.md"


def post_routes():
    tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
    routes = []

    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        for decorator in node.decorator_list:
            if not (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and isinstance(decorator.func.value, ast.Name)
                and decorator.func.value.id == "app"
                and decorator.func.attr == "post"
                and decorator.args
                and isinstance(decorator.args[0], ast.Constant)
            ):
                continue

            routes.append((decorator.args[0].value, node.name))

    return routes


class PostRouteTests(unittest.TestCase):
    def test_post_handlers_have_unique_function_names(self):
        handler_names = [handler for _, handler in post_routes()]

        self.assertEqual(len(handler_names), len(set(handler_names)))

    def test_unused_generate_route_is_removed(self):
        routes = post_routes()

        self.assertNotIn("/api/generate", [path for path, _ in routes])
        self.assertIn(("/api/generate-project", "generate_project_archive"), routes)

    def test_api_docs_describe_the_retained_archive_route(self):
        api_docs = API_DOC_PATH.read_text(encoding="utf-8")

        self.assertIn("**POST** `/api/generate-project`", api_docs)
        self.assertNotIn("`/api/generate`", api_docs)


if __name__ == "__main__":
    unittest.main()
