import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [requirement.strip() for requirement in  open("requirements.txt").readlines()]
    
setuptools.setup(
    name="KnowledgeSimulator", # Replace with your own username
    version="0.0.1",
    author="Justin Jose",
    install_requires = requirements,
    author_email="justinj@thoughtworks.com",
    description="Simulate logic state transistion on knowledge repo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/t3pleni9/KnowledgeSimulator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
