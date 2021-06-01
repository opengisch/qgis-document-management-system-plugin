# Document Management System plugin for QGIS

## What
A document management plugin to help managing relations between a documents table and features.

## Configuration

### Document side

![Configuration document side](docs/images/ConfigurationDocumentSideScreenshot.png)

#### Widget type
Set to *Document relation editor (Document side)*

#### Relation to features
* Normal one to many
  * Set cardinality to *Many to one relation*
  * Uncheck *Polymorphic relation*
* Normal many to many
  * Set cardinality to the final table
  * Uncheck *Polymorphic relation*
* Polymorphic
  * Set cardinality to *Many to one relation*
  * Check *Polymorphic relation*
  * Select the right polymorphic relation with the selection box

### Feature side

![Configuration feature side](docs/images/ConfigurationFeatureSideScreenshot.png)

#### Widget type
Set to *Document relation editor (Feature side)*

#### Relation to documents
* Normal one to many
  * Set cardinality to *Many to one relation*
* Normal many to many
  * Set cardinality to the document table
  
#### Widget configuration

* **Document path:** An expression to the default path for documents.
* **Document filename:** The field containing the document filename.
* **Document author:** An expression for the author of the document.


## Usage

### Document side

![Configuration feature side](docs/images/WidgetDocumentSideScreencast.gif)

### Feature side

![Configuration feature side](docs/images/WidgetFeatureSideScreencast.gif)
