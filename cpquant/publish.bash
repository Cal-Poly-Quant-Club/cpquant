git push
git tag $1
git push --tags
poetry build
poetry publish -r test-pypi
poety publish