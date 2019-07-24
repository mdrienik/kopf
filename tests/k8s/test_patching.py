import aiohttp.web
import pytest

from kopf.clients.patching import patch_obj


@pytest.mark.resource_clustered  # see `resp_mocker`
async def test_by_name_clustered(
        resp_mocker, aresponses, hostname, resource):

    patch_mock = resp_mocker(return_value=aiohttp.web.json_response({}))
    aresponses.add(hostname, resource.get_url(namespace=None, name='name1'), 'patch', patch_mock)

    patch = {'x': 'y'}
    await patch_obj(resource=resource, namespace=None, name='name1', patch=patch)

    assert patch_mock.called
    assert patch_mock.call_count == 1

    data = patch_mock.call_args_list[0][0][0].data  # [callidx][args/kwargs][argidx]
    assert data == {'x': 'y'}


async def test_by_name_namespaced(
        resp_mocker, aresponses, hostname, resource):

    patch_mock = resp_mocker(return_value=aiohttp.web.json_response({}))
    aresponses.add(hostname, resource.get_url(namespace='ns1', name='name1'), 'patch', patch_mock)

    patch = {'x': 'y'}
    await patch_obj(resource=resource, namespace='ns1', name='name1', patch=patch)

    assert patch_mock.called
    assert patch_mock.call_count == 1

    data = patch_mock.call_args_list[0][0][0].data  # [callidx][args/kwargs][argidx]
    assert data == {'x': 'y'}


@pytest.mark.resource_clustered  # see `resp_mocker`
async def test_by_body_clustered(
        resp_mocker, aresponses, hostname, resource):

    patch_mock = resp_mocker(return_value=aiohttp.web.json_response({}))
    aresponses.add(hostname, resource.get_url(namespace=None, name='name1'), 'patch', patch_mock)

    patch = {'x': 'y'}
    body = {'metadata': {'name': 'name1'}}
    await patch_obj(resource=resource, body=body, patch=patch)

    assert patch_mock.called
    assert patch_mock.call_count == 1

    data = patch_mock.call_args_list[0][0][0].data  # [callidx][args/kwargs][argidx]
    assert data == {'x': 'y'}


async def test_by_body_namespaced(
        resp_mocker, aresponses, hostname, resource):

    patch_mock = resp_mocker(return_value=aiohttp.web.json_response({}))
    aresponses.add(hostname, resource.get_url(namespace='ns1', name='name1'), 'patch', patch_mock)

    patch = {'x': 'y'}
    body = {'metadata': {'namespace': 'ns1', 'name': 'name1'}}
    await patch_obj(resource=resource, body=body, patch=patch)

    assert patch_mock.called
    assert patch_mock.call_count == 1

    data = patch_mock.call_args_list[0][0][0].data  # [callidx][args/kwargs][argidx]
    assert data == {'x': 'y'}


async def test_raises_when_body_conflicts_with_namespace(
        resp_mocker, aresponses, hostname, resource):

    patch_mock = resp_mocker(return_value=aiohttp.web.json_response())
    aresponses.add(hostname, resource.get_url(namespace=None, name='name1'), 'patch', patch_mock)
    aresponses.add(hostname, resource.get_url(namespace='ns1', name='name1'), 'patch', patch_mock)

    patch = {'x': 'y'}
    body = {'metadata': {'namespace': 'ns1', 'name': 'name1'}}
    with pytest.raises(TypeError):
        await patch_obj(resource=resource, body=body, namespace='ns1', patch=patch)

    assert not patch_mock.called


async def test_raises_when_body_conflicts_with_name(
        resp_mocker, aresponses, hostname, resource):

    patch_mock = resp_mocker(return_value=aiohttp.web.json_response())
    aresponses.add(hostname, resource.get_url(namespace=None, name='name1'), 'patch', patch_mock)
    aresponses.add(hostname, resource.get_url(namespace='ns1', name='name1'), 'patch', patch_mock)

    patch = {'x': 'y'}
    body = {'metadata': {'namespace': 'ns1', 'name': 'name1'}}
    with pytest.raises(TypeError):
        await patch_obj(resource=resource, body=body, name='name1', patch=patch)

    assert not patch_mock.called


async def test_raises_when_body_conflicts_with_ids(
        resp_mocker, aresponses, hostname, resource):

    patch_mock = resp_mocker(return_value=aiohttp.web.json_response())
    aresponses.add(hostname, resource.get_url(namespace=None, name='name1'), 'patch', patch_mock)
    aresponses.add(hostname, resource.get_url(namespace='ns1', name='name1'), 'patch', patch_mock)

    patch = {'x': 'y'}
    body = {'metadata': {'namespace': 'ns1', 'name': 'name1'}}
    with pytest.raises(TypeError):
        await patch_obj(resource=resource, body=body, namespace='ns1', name='name1', patch=patch)

    assert not patch_mock.called


@pytest.mark.parametrize('namespace', [None, 'ns1'], ids=['without-namespace', 'with-namespace'])
@pytest.mark.parametrize('status', [404])
async def test_ignores_absent_objects(
        resp_mocker, aresponses, hostname, resource, namespace, status):

    patch_mock = resp_mocker(return_value=aresponses.Response(status=status, reason="boo!"))
    aresponses.add(hostname, resource.get_url(namespace=None, name='name1'), 'patch', patch_mock)
    aresponses.add(hostname, resource.get_url(namespace='ns1', name='name1'), 'patch', patch_mock)

    patch = {'x': 'y'}
    body = {'metadata': {'namespace': namespace, 'name': 'name1'}}
    await patch_obj(resource=resource, body=body, patch=patch)


@pytest.mark.parametrize('namespace', [None, 'ns1'], ids=['without-namespace', 'with-namespace'])
@pytest.mark.parametrize('status', [400, 401, 403, 500, 666])
async def test_raises_api_errors(
        resp_mocker, aresponses, hostname, resource, namespace, status):

    patch_mock = resp_mocker(return_value=aresponses.Response(status=status, reason="boo!"))
    aresponses.add(hostname, resource.get_url(namespace=None, name='name1'), 'patch', patch_mock)
    aresponses.add(hostname, resource.get_url(namespace='ns1', name='name1'), 'patch', patch_mock)

    patch = {'x': 'y'}
    body = {'metadata': {'namespace': namespace, 'name': 'name1'}}
    with pytest.raises(aiohttp.ClientResponseError) as e:
        await patch_obj(resource=resource, body=body, patch=patch)
    assert e.value.status == status
