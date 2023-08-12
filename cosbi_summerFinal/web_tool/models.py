# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class GeneTable(models.Model):
    gene_id = models.TextField(db_column='Gene_ID', primary_key=True, blank=True)  # Field name made lowercase.
    transcript_id = models.TextField(db_column='transcript_ID', blank=True, null=True)  # Field name made lowercase.
    field_oftranscripts = models.IntegerField(db_column='#oftranscripts', blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it started with '_'.

    class Meta:
        managed = False
        db_table = 'gene_table'
