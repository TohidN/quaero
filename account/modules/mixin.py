from django.db import models


class NaiveHierarchyManager(models.Manager):
	def get_roots(self):
		return self.get_query_set().filter(parent__isnull=True)


class NaiveHierarchy(models.Model):
	parent = models.ForeignKey('self', null=True, blank=True)
	tree = NaiveHierarchyManager()

	def get_children(self):
		return self._default_manager.filter(parent=self)

	def get_descendants(self):
		descendants = set(self.get_children())
		for node in list(descendants):
			descendants.update(node.get_descendants())
		return descendants

	class Meta:
		abstract = True
