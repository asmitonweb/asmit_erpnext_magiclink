from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

from asmit_erpnext_magiclink import __version__ as version

setup(
	name="asmit_erpnext_magiclink",
	version=version,
	description="Generic Magic Link Login for ERPNext",
	author="Asmit Anand Singh",
	author_email="asmitanandsingh.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
