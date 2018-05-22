# ckanext-odm_dataset-ext
=================

A CKAN extension which provides with data definition and logic for datasets in respect to ISO19115

# Installation

In order to install this CKAN Extension:

  * clone the ckanext-odm_dataset-ext folder to the src/ folder in the target CKAN instance. NOTE: This repository contains some submodules, hence do not forget to include the --recursive flag for the git clone.

 ```
 git clone --recursive https://github.com/derilinx/ckanext-odm_dataset-ext.git
 cd ckanext-odm_dataset-ext
 ```

 * Install dependencies
 <code>pip install -r requirements.txt</code>

 * Setup plugin
 <code>python setup.py develop</code>


# Copyright and License

This material is copyright (c) 2018 Derilinx Ltd.

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
