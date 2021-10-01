from setuptools import setup, find_packages


setup(
    name="rweb_datatable",
    version="0.1.9",
    author="Steve McCartney",
    author_email="python+rweb_datatable@reconvergent.com",
    url="https://github.com/stevemccartney/rweb_datatable",
    packages=find_packages(),
    license="Apache-2.0",
    description="Server-side datatables rendered to HTML using htmx",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
        "Typing :: Typed",
    ],
)