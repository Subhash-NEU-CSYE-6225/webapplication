## `Steps to run the project`

- Fork the organization repo to your profile
- Clone the repository using git clone `repository link`
- Checkout to your own branch by running `git checkout -b <BRANCH_NAME>`
- Add a simple change and update it in your branch
- On creating a pull request, the github actions will run and create an ami using packer
- Copy the ami id and run infrastructure code which will create an Ec2 instance