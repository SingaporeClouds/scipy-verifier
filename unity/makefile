# ==========================================
#   Unity Project - A Test Framework for C
#   Copyright (c) 2007 Mike Karlesky, Mark VanderVoord, Greg Williams
#   [Released under MIT License. Please refer to license.txt for details]
# ========================================== 

C_COMPILER=gcc
ifeq ($(OS),Windows_NT)
	TARGET_EXTENSION=.exe
else
	TARGET_EXTENSION=.out
endif
TARGET = out/$(TARGET_BASE)$(TARGET_EXTENSION)
OUT_FILE=-o $(TARGET)

SRC_FILES=src/unity.c test/$(TARGET_BASE).c build/$(TARGET_BASE).c
INC_DIRS=-Isrc
SYMBOLS=-DTEST -DUNITY_SUPPORT_64

ifeq ($(OS),Windows_NT)
	CLEANUP = del /F /Q build\* && del /F /Q $(TARGET)
else
	CLEANUP = rm -f build/*.o ; rm -f $(TARGET)
endif

all: clean default

default:
	ruby auto/generate_test_runner.rb test/$(TARGET_BASE).c build/$(TARGET_BASE).c
	$(C_COMPILER) $(INC_DIRS) $(SYMBOLS) $(SRC_FILES) $(OUT_FILE)
	chmod +x $(TARGET)	
	./$(TARGET)

clean:
	$(CLEANUP)
	
