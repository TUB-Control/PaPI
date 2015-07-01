
UIPY = pyuic5

SRC_DIR = ./ui/

DES_DIR = ./papi/

UI_FILES = quitter.ui

MD_SRC_DIR = papi
MD_DES_DIR = docs

UI_FILES_FOUND = $(shell find $(SRC_DIR) -name '*.ui')
UI_FILES = $(UI_FILES_FOUND:./%=%)
PY_FILES = $(addprefix $(DES_DIR),$(UI_FILES:.ui=.py))

#Find all rst files
MD_FILES_SRC = $(shell find $(MD_SRC_DIR) -name '*.rst')

#Create target names
MD_FILES_TAR_TMP := $(subst /,., $(MD_FILES_SRC))
MD_FILES_TAR_TMP2 := $(subst ..,./, $(MD_FILES_TAR_TMP))
MD_FILES_TAR := $(MD_FILES_TAR_TMP2:.rst=.rst)
MD_TAR :=  $(addprefix $(MD_DES_DIR)/,$(MD_FILES_TAR))

MKDIR_P = mkdir -p

AUTHOR = $(shell whoami)

.PHONY: md_files create_rst create_ui clean

create_ui: $(PY_FILES)

$(PY_FILES): $(UI_FILES)

$(UI_FILES):

	mkdir -p $(DES_DIR)$(dir $@)
	$(UIPY) $@ -o $(DES_DIR)$(dir $@)$(notdir $(basename $@)).py

	@if [ -f $(DES_DIR)$(dir $@)__init__.py ] ; \
	then echo "__init__.py exists"  ; \
	else echo "__author__ = '$(AUTHOR)'" > $(DES_DIR)$(dir $@)__init__.py  ; \
	fi 

md_files: $(MD_TAR)

$(MD_DES_DIR)/%.rst: $(MD_FILES_SRC)
	$(eval rst_name:= $(subst $(MD_DES_DIR),.,$(subst /rst,.rst,$(subst .,/, $@))))
	@echo "Creating file" $@
	$(eval arr:= $(shell echo $(subst $(MD_DES_DIR)/,,$(@:.rst=)) | tr "." "\n"))

	@cp $(rst_name) $@

 
create_rst: $(MD_TAR)
	sphinx-apidoc -f -o docs papi ./papi/pyqtgraph/ ./papi/yapsy/

docs: create_rst
	make -C docs html

html: create_rst
	make -C docs html

clean:
	@rm $(MD_DES_DIR)/papi*rst
	@rm $(MD_DES_DIR)/plugin*rst
	@rm $(MD_DES_DIR)/modules.rst
	make -C docs clean
