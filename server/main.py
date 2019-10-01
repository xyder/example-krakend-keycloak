# pylint: disable=no-member

import uuid
from dataclasses import asdict, dataclass

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound
import faker


@dataclass
class Parent:
    data: dict


@dataclass
class Sibling:
    data: dict


@dataclass
class Child:
    data: dict


@dataclass
class Database:
    parents: dict
    siblings: dict
    children: dict


def generate_database():
    no_parents = 100
    fake = faker.Faker()

    parents = dict()
    siblings = dict()
    children = dict()
    parent_ids = list()

    for _ in range(0, no_parents):
        parent_id = str(uuid.uuid4())

        parent_ids.append(parent_id)
        parents[parent_id] = Parent({
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'address': fake.address(),
            'super_secret_field': 'super_secret_value'
        })
        siblings[parent_id] = Sibling({
            'website': fake.uri(),
            'email': fake.email(),
        })

    for _ in range(0, int(no_parents/2)):
        children[str(uuid.uuid4())] = Child({
            # only the first 10 to increase chances of having multiple children .. that sounded weird
            'parent_id': parent_ids[fake.pyint(min_value=0, max_value=10, step=1)],
            'color': fake.color_name(),
            'license': fake.license_plate(),
            'produced': fake.iso8601(),
        })

    return Database(parents=parents, children=children, siblings=siblings)


database = generate_database()


def lister_getter(request, path_key, items_db):
    item_id = request.match_info.get(path_key, None)
    if not item_id:
        return web.json_response(
            {
                'content': [dict(id=k, **v.data) for k, v in items_db.items()],
                'hidden_children_field': 'hidden_value'
            })

    if item_id not in items_db:
        raise HTTPNotFound()

    data = dict()
    data[path_key] = item_id
    data.update(items_db[item_id].data)
    return web.json_response(data)


async def list_parents(request):
    print(request.headers)
    return lister_getter(request, 'parent_id', database.parents)


async def list_siblings(request):
    return lister_getter(request, 'sibling_id', database.siblings)


async def list_children(request):
    return lister_getter(request, 'child_id', database.children)


async def children_for_parent(request):
    parent_id = request.match_info.get('parent_id', None)

    if not parent_id:
        raise HTTPNotFound()

    children = {k: v for k, v in database.children.items() if v.data['parent_id'] == parent_id}
    return lister_getter(request, 'dummy', children)


def main():
    app = web.Application()
    app.add_routes([
        web.get('/parents', list_parents),
        web.get('/parents/{parent_id}', list_parents),
        web.get('/parents/{parent_id}/children', children_for_parent),
        web.get('/siblings', list_siblings),
        web.get('/siblings/{sibling_id}', list_siblings),
        web.get('/children', list_children),
        web.get('/children/{child_id}', list_children),
    ])

    web.run_app(app, port=8400)

if __name__ == '__main__':
    main()
