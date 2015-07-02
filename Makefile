
UIPY = pyuic5

SRC_DIR = ./ui/

DES_DIR = ./papi/

UI_FILES = quitter.ui

MD_SRC_DIR := papi
MD_DES_DIR := docs

MD_STATIC_FOLDER_SRC := _static
MD_STATIC_FOLDER_DES := $(MD_DES_DIR)/_static

UI_FILES_FOUND := $(shell find $(SRC_DIR) -name '*.ui')
UI_FILES := $(UI_FILES_FOUND:./%=%)
PY_FILES := $(addprefix $(DES_DIR),$(UI_FILES:.ui=.py))

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
	$(MKDIR_P) $(MD_STATIC_FOLDER_DES)
#	Copy rst files
	$(eval rst_name:= $(subst $(MD_DES_DIR),.,$(subst /rst,.rst,$(subst .,/, $@))))
	@echo "Creating file" $@
#	$(eval arr:= $(shell echo $(subst $(MD_DES_DIR)/,,$(@:.rst=)) | tr "." "\n"))
#	@echo "Creating file" $@ "<-" $(rst_name)
	@cp $(rst_name) $@
#   Copy _static files
	$(eval static_folder_src:= $(dir $(rst_name))$(MD_STATIC_FOLDER_SRC)/)
	
	$(eval dir_rst_tmp:=$(dir $(rst_name)))
	$(eval dir_rst:=$(dir_rst_tmp:/=))
	$(eval unique_name:= $(notdir $(dir_rst)))
	
#	$(eval files_to_cp := $(shell find $(static_folder_src) -type f -printf "%f\n"))	
	
	@echo "Copy static files from" $(static_folder_src) "to" $(MD_STATIC_FOLDER_DES)/
	@if [ -d $(static_folder_src) ] ; then \
	echo "->" $(unique_name) ; \
	sed -i s,$(MD_STATIC_FOLDER_SRC),$(MD_STATIC_FOLDER_SRC)/$(unique_name),g $@ ; \
	$(MKDIR_P) $(MD_STATIC_FOLDER_DES)/$(unique_name) ; \
	cp -Rp $(static_folder_src)* $(MD_STATIC_FOLDER_DES)/$(unique_name)/ ; \
	fi
	
#	@if [ -d $(static_folder_src) ] ; \
#	then echo "static exists" ; \
#		files_to_cp= find $(static_folder_src) -type f -printf "%f\n" ; \
#		echo ":" $(files_to_cp) ; \
#		for file in $(files_to_cp); do  \
#			echo "->" $(file) ; \
#			if [ -d $(file) ] ; then \
#				echo $(file) ; \
#			fi ; \
#		done ; \
#	fi
	
#	$(eval files_to_cp := $(shell find $(static_folder_src) -name '*'))
#	@echo "cp files " $(files_to_cp)	
#	@echo "Copy static files from" $(static_folder_src) "to" $(MD_STATIC_FOLDER_DES)/
#	@$(foreach file,$(files_to_cp),echo $(file);)

create_rst: $(MD_TAR)
	sphinx-apidoc -f -o docs papi ./papi/pyqtgraph/ ./papi/yapsy/

docs: create_rst
	make -C docs html

html: create_rst
	make -C docs html

clean:
	@rm $(MD_DES_DIR)/papi*rst
	@rm $(MD_DES_DIR)/modules.rst
	@rm -R $(MD_STATIC_FOLDER_DES)
	make -C docs clean
