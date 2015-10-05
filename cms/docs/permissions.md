Permissions
===========

The CMS uses a list of permissions to permit specific for each user. By default,
a superuser will have all permissions, while a staff user will have none.
A superuser needs to create a Role and pre-assign permissions to that role.
Then a role can be assigned to a user to give it the permission set inside 
that role.


## Page permissions

| Permissions      | Codename         |
|------------------|------------------|
| Can add Page     | cms.add_page     |
| Can change Page  | cms.change_page  |
| Can delete Page  | cms.delete_page  |
| Can publish Page | cms.publish_page |


## Page translations permissions

| Permissions             | Codename                    |
|-------------------------|-----------------------------|
| Can add Translation     | cms.add_pagetranslation     |
| Can change Translation  | cms.change_pagetranslation  |
| Can delete Translation  | cms.delete_pagetranslation  |
| Can publish Translation | cms.publish_pagetranslation |


## Page dataset translations

| Permissions               | Codename                |
|---------------------------|-------------------------|
| Can add Page data set     | cms.add_pagedataset     |
| Can change Page data set  | cms.change_pagedataset  |
| Can delete Page data set  | cms.delete_pagedataset  |
| Can publish Page data set | cms.publish_pagedataset |