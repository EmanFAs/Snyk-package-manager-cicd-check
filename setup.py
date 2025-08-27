from setuptools import setup, find_packages

setup(
    name="snyk-package-manager-cicd-check-and-report",
    version="0.1.0",
    author="Fritz Abélard",
    author_email="fritz.abelard@snyk.io",
    description="Python scripts for Snyk CI/CD gating and API-driven reporting.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/EmanFAs/Snyk-package-manager-cicd-check",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests==2.32.4",
        "packaging",
    ],
)
