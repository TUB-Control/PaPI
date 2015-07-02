
UIPY = pyuic5

SRC_DIR = ./ui/

DES_DIR = ./papi/

UI_FILES = quitter.ui

RST_SRC_DIR := papi
RST_DES_DIR := docs

RST_STATIC_FOLDER_SRC := _static
RST_STATIC_FOLDER_DES := $(RST_DES_DIR)/_static

UI_FILES_FOUND := $(shell find $(SRC_DIR) -name '*.ui')
UI_FILES := $(UI_FILES_FOUND:./%=%)
PY_FILES := $(addprefix $(DES_DIR),$(UI_FILES:.ui=.py))

#Find all rst files
RST_FILES_SRC = $(shell find $(RST_SRC_DIR) -name '*.rst')

#Create target names
RST_FILES_TAR_TMP := $(subst /,., $(RST_FILES_SRC))
RST_FILES_TAR_TMP2 := $(subst ..,./, $(RST_FILES_TAR_TMP))
RST_FILES_TAR := $(RST_FILES_TAR_TMP2:.rst=.rst)
RST_TAR :=  $(addprefix $(RST_DES_DIR)/,$(RST_FILES_TAR))

MKDIR_P = mkdir -p

AUTHOR = $(shell whoami)

.PHONY: rst_files create_rst create_ui clean

create_ui: $(PY_FILES)

$(PY_FILES): $(UI_FILES)

$(UI_FILES):

	mkdir -p $(DES_DIR)$(dir $@)
	$(UIPY) $@ -o $(DES_DIR)$(dir $@)$(notdir $(basename $@)).py

	@if [ -f $(DES_DIR)$(dir $@)__init__.py ] ; \
	then echo "__init__.py exists"  ; \
	else echo "__author__ = '$(AUTHOR)'" > $(DES_DIR)$(dir $@)__init__.py  ; \
	fi 

rst_files: $(RST_TAR)

$(RST_DES_DIR)/%.rst: $(RST_FILES_SRC)
	
	@if [ ! -d $(RST_STATIC_FOLDER_DES) ] ; then \
	$(MKDIR_P) $(RST_STATIC_FOLDER_DES) ; \
	fi
#	Copy rst files
	$(eval rst_name:= $(subst $(RST_DES_DIR),.,$(subst /rst,.rst,$(subst .,/, $@))))
	@echo "Creating file" $@
#	$(eval arr:= $(shell echo $(subst $(RST_DES_DIR)/,,$(@:.rst=)) | tr "." "\n"))
#	@echo "Creating file" $@ "<-" $(rst_name)
	@cp $(rst_name) $@
#   Copy _static files
	$(eval static_folder_src:= $(dir $(rst_name))$(RST_STATIC_FOLDER_SRC)/)
	
	$(eval dir_rst_tmp:=$(dir $(rst_name)))
	$(eval dir_rst:=$(dir_rst_tmp:/=))
	$(eval unique_name:= $(notdir $(dir_rst)))
	
#	$(eval files_to_cp := $(shell find $(static_folder_src) -type f -printf "%f\n"))	
	
#	@echo "Copy static files from" $(static_folder_src) "to" $(RST_STATIC_FOLDER_DES)/
	@if [ -d $(static_folder_src) ] ; then \
	sed -i s,$(RST_STATIC_FOLDER_SRC),$(RST_STATIC_FOLDER_SRC)/$(unique_name),g $@ ; \
	$(MKDIR_P) $(RST_STATIC_FOLDER_DES)/$(unique_name) ; \
	cp -Rp $(static_folder_src)* $(RST_STATIC_FOLDER_DES)/$(unique_name)/ ; \
	fi
	
create_rst: $(RST_TAR)
	sphinx-apidoc -f -o docs papi ./papi/pyqtgraph/ ./papi/yapsy/

docs: create_rst
	make -C docs html

html: create_rst
	make -C docs html

clean:
	@rm $(RST_DES_DIR)/papi*rst
	@rm $(RST_DES_DIR)/modules.rst
	@rm -R $(RST_STATIC_FOLDER_DES)
	make -C docs clean
