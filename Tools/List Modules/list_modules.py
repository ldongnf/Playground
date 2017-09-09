import pip

installed_packages = pip.get_installed_distributions()
installed_packages_list = sorted(["%s == %s" % (i.key, i.version) for i in installed_packages], reverse=False)

print
for package in installed_packages_list:
	print package
print