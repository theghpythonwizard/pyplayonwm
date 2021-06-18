from setuptools import setup, find_packages

install_requires = [
    "tox==3.23.1",
    "pytest==6.2.4"
]

setup(
    name="pyplayonwm",
    version="0.0.1",
    description="package to help remove the playon watermark from a video file with handbrake",
    author="Jason Schultheis",
    author_email="pressurechief@outlook.com",
    license="MIT",
    url="https://github.com/theghpythonwizard/pyplayonwm",
    zip_safe=True,
    packages=['pyplayonwm'],
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 5 - Test',
        'License :: OSI Approved :: GNU License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ]
)