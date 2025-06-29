from setuptools import setup, find_packages
setup(
    name='geometrictrading',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=['numpy', 'scipy', 'pandas', 'plotly', 'ccxt', 'pytest'],
    author='symbioticode',
    description='Geometric Trading based on TGE',
    license='MIT with Ethical Clause',
)
