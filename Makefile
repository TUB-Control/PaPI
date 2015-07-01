
UIPY = pyuic5

SRC_DIR = ./ui/

DES_DIR = ./papi/

UI_FILES = quitter.ui

MD_SRC_DIR = ./papi/
MD_DES_DIR = ./docs/

UI_FILES_FOUND = $(shell find $(SRC_DIR) -name '*.ui')
UI_FILES = $(UI_FILES_FOUND:./%=%)
PY_FILES = $(addprefix $(DES_DIR),$(UI_FILES:.ui=.py))

MD_FILES_FOUND = $(shell find $(MD_SRC_DIR) -name '*.rst')

MKDIR_P = mkdir -p

AUTHOR = $(shell whoami)

#all: $(UI_FILES)

all:

create_ui: $(PY_FILES)

$(PY_FILES): $(UI_FILES)

$(UI_FILES):

	mkdir -p $(DES_DIR)$(dir $@)
	$(UIPY) $@ -o $(DES_DIR)$(dir $@)$(notdir $(basename $@)).py

	@if [ -f $(DES_DIR)$(dir $@)__init__.py ] ; \
	then echo "__init__.py exists"  ; \
	else echo "__author__ = '$(AUTHOR)'" > $(DES_DIR)$(dir $@)__init__.py  ; \
	fi 

$(MD_FILES_FOUND):
	@echo "MD_FILES_FOUND" $@

	$(eval rst_name:= $(subst /,., $@))

	@echo "->" $(rst_name)

	cp $@ $(MD_DES_DIR)$(rst_name)
 
create_rst: $(MD_FILES_FOUND)
	sphinx-apidoc -f -o docs papi ./papi/pyqtgraph/ ./papi/yapsy/



docs: create_rst
	make -C docs html

html:
	make -C docs html
