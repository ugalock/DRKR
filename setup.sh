#!/usr/bin/env bash
#
# Bash script to remove old frontend files/directories and create the new ones
# based on the updated DRKR frontend structure.
#
# WARNING: This will permanently remove certain files/folders. Make a backup or
# ensure you’re using version control (Git) before proceeding.

# 1) Remove old files
rm -f \
  frontend/src/index.js \
  frontend/src/App.js \
  frontend/src/App.css \
  frontend/src/routes.js \
  frontend/src/services/api.js

# 2) Remove old directories
rm -rf \
  frontend/src/components/Auth \
  frontend/src/components/Prompts \
  frontend/src/components/ResearchJobs

rm -f \
  frontend/src/pages/Home.js \
  frontend/src/pages/PromptsPage.js \
  frontend/src/pages/PromptDetail.js \
  frontend/src/pages/ResearchJobDetail.js \
  frontend/src/pages/UserProfile.js

# 3) Create new folders
mkdir -p frontend/src/{assets,components/{common},pages/{Home,Auth,Research,Organization,Tags},features/{deepResearch,tags,organizations,search},routes,services/api,store,hooks,context,utils,types}

# 4) Create new files (touch only if they don't already exist)
touch \
  frontend/src/main.tsx \
  frontend/src/App.tsx \
  frontend/src/index.css \
  frontend/src/routes/index.tsx \
  frontend/src/services/api/axiosConfig.ts \
  frontend/src/services/api/userApi.ts \
  frontend/src/services/api/researchApi.ts \
  frontend/src/services/api/tagsApi.ts \
  frontend/src/services/queryClient.ts \
  frontend/src/services/authService.ts \
  frontend/src/store/userStore.ts \
  frontend/src/hooks/useAuth.ts \
  frontend/src/hooks/useFetchOrg.ts \
  frontend/src/context/AuthContext.tsx \
  frontend/src/context/OrgContext.tsx \
  frontend/src/utils/constants.ts \
  frontend/src/utils/formatters.ts \
  frontend/src/types/index.d.ts \
  frontend/src/types/user.d.ts \
  frontend/src/types/research.d.ts \
  frontend/src/types/org.d.ts \
  frontend/src/vite-env.d.ts

echo "Old files/folders removed, and new structure created (if not already present)."
