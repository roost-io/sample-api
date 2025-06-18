const axios = require('axios');
const crypto = require('crypto');

class BambooHROktaProvisioning {
    constructor(bambooHRConfig, oktaConfig) {
        this.bambooHR = {
            subdomain: bambooHRConfig.subdomain,
            apiKey: bambooHRConfig.apiKey,
            baseURL: `https://api.bamboohr.com/api/gateway.php/${bambooHRConfig.subdomain}/v1`
        };
        
        this.okta = {
            domain: oktaConfig.domain,
            apiToken: oktaConfig.apiToken,
            baseURL: `https://${oktaConfig.domain}/api/v1`
        };
        
        this.bambooHRClient = axios.create({
            baseURL: this.bambooHR.baseURL,
            auth: {
                username: this.bambooHR.apiKey,
                password: 'x'
            },
            headers: {
                'Accept': 'application/json'
            }
        });
        
        this.oktaClient = axios.create({
            baseURL: this.okta.baseURL,
            headers: {
                'Authorization': `SSWS ${this.okta.apiToken}`,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
    }

    /**
     * Fetch employees from BambooHR
     * @param {Array} fields - Fields to retrieve
     * @returns {Promise<Array>} Array of employee objects
     */
    async fetchBambooHREmployees(fields = ['firstName', 'lastName', 'workEmail', 'department', 'jobTitle', 'employeeNumber', 'status']) {
        try {
            console.log('Fetching employees from BambooHR...');
            
            const response = await this.bambooHRClient.get('/employees/directory', {
                params: {
                    fields: fields.join(',')
                }
            });
            
            const employees = response.data.employees || [];
            console.log(`Retrieved ${employees.length} employees from BambooHR`);
            
            return employees.filter(emp => emp.workEmail && emp.status === 'Active');
        } catch (error) {
            console.error('Error fetching BambooHR employees:', error.message);
            throw error;
        }
    }

    /**
     * Check if user exists in Okta
     * @param {string} email - User email
     * @returns {Promise<Object|null>} Okta user object or null
     */
    async checkOktaUserExists(email) {
        try {
            const response = await this.oktaClient.get(`/users/${encodeURIComponent(email)}`);
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 404) {
                return null;
            }
            throw error;
        }
    }

    /**
     * Generate a temporary password
     * @returns {string} Temporary password
     */
    generateTemporaryPassword() {
        return crypto.randomBytes(12).toString('base64').slice(0, 12) + 'Aa1!';
    }

    /**
     * Create Okta user profile from BambooHR employee data
     * @param {Object} employee - BambooHR employee object
     * @returns {Object} Okta user profile
     */
    createOktaUserProfile(employee) {
        return {
            profile: {
                firstName: employee.firstName,
                lastName: employee.lastName,
                email: employee.workEmail,
                login: employee.workEmail,
                employeeNumber: employee.employeeNumber || employee.id,
                title: employee.jobTitle,
                department: employee.department,
                primaryPhone: employee.mobilePhone || employee.homePhone,
                manager: employee.supervisor
            },
            credentials: {
                password: {
                    value: this.generateTemporaryPassword()
                }
            },
            groupIds: [], // Add relevant group IDs based on department/role
            activate: true
        };
    }

    /**
     * Create user in Okta
     * @param {Object} userProfile - Okta user profile
     * @returns {Promise<Object>} Created Okta user
     */
    async createOktaUser(userProfile) {
        try {
            const response = await this.oktaClient.post('/users', userProfile);
            console.log(`Created Okta user: ${userProfile.profile.email}`);
            return response.data;
        } catch (error) {
            console.error(`Error creating Okta user ${userProfile.profile.email}:`, error.response?.data || error.message);
            throw error;
        }
    }

    /**
     * Update existing Okta user
     * @param {string} userId - Okta user ID
     * @param {Object} profile - Updated profile data
     * @returns {Promise<Object>} Updated Okta user
     */
    async updateOktaUser(userId, profile) {
        try {
            const response = await this.oktaClient.post(`/users/${userId}`, { profile });
            console.log(`Updated Okta user: ${profile.email}`);
            return response.data;
        } catch (error) {
            console.error(`Error updating Okta user ${profile.email}:`, error.response?.data || error.message);
            throw error;
        }
    }

    /**
     * Assign user to groups based on department or role
     * @param {string} userId - Okta user ID
     * @param {string} department - Employee department
     * @param {string} jobTitle - Employee job title
     */
    async assignUserToGroups(userId, department, jobTitle) {
        try {
            // Define department to group mappings
            const departmentGroups = {
                'Engineering': 'ENGINEERING_GROUP_ID',
                'Human Resources': 'HR_GROUP_ID',
                'Sales': 'SALES_GROUP_ID',
                'Marketing': 'MARKETING_GROUP_ID',
                'Finance': 'FINANCE_GROUP_ID'
            };

            const groupId = departmentGroups[department];
            if (groupId) {
                await this.oktaClient.put(`/groups/${groupId}/users/${userId}`);
                console.log(`Assigned user ${userId} to group ${department}`);
            }

            // Assign manager role if applicable
            if (jobTitle && jobTitle.toLowerCase().includes('manager')) {
                await this.oktaClient.put(`/groups/MANAGERS_GROUP_ID/users/${userId}`);
                console.log(`Assigned user ${userId} to managers group`);
            }
        } catch (error) {
            console.error(`Error assigning groups to user ${userId}:`, error.response?.data || error.message);
        }
    }

    /**
     * Main provisioning function
     * @param {Object} options - Provisioning options
     */
    async provisionUsers(options = {}) {
        const { dryRun = false, updateExisting = true } = options;
        
        try {
            console.log('Starting BambooHR to Okta user provisioning...');
            
            const employees = await this.fetchBambooHREmployees();
            const results = {
                processed: 0,
                created: 0,
                updated: 0,
                errors: 0,
                errorDetails: []
            };

            for (const employee of employees) {
                try {
                    results.processed++;
                    console.log(`Processing employee: ${employee.firstName} ${employee.lastName} (${employee.workEmail})`);

                    if (dryRun) {
                        console.log(`[DRY RUN] Would process: ${employee.workEmail}`);
                        continue;
                    }

                    const existingUser = await this.checkOktaUserExists(employee.workEmail);
                    
                    if (existingUser) {
                        if (updateExisting) {
                            const updatedProfile = this.createOktaUserProfile(employee).profile;
                            await this.updateOktaUser(existingUser.id, updatedProfile);
                            results.updated++;
                        } else {
                            console.log(`User ${employee.workEmail} already exists, skipping...`);
                        }
                    } else {
                        const userProfile = this.createOktaUserProfile(employee);
                        const newUser = await this.createOktaUser(userProfile);
                        
                        // Assign to groups
                        await this.assignUserToGroups(newUser.id, employee.department, employee.jobTitle);
                        
                        results.created++;
                    }

                    // Rate limiting - wait between requests
                    await new Promise(resolve => setTimeout(resolve, 200));

                } catch (error) {
                    results.errors++;
                    results.errorDetails.push({
                        employee: `${employee.firstName} ${employee.lastName}`,
                        email: employee.workEmail,
                        error: error.message
                    });
                    console.error(`Error processing ${employee.workEmail}:`, error.message);
                }
            }

            console.log('\n=== Provisioning Summary ===');
            console.log(`Processed: ${results.processed}`);
            console.log(`Created: ${results.created}`);
            console.log(`Updated: ${results.updated}`);
            console.log(`Errors: ${results.errors}`);
            
            if (results.errorDetails.length > 0) {
                console.log('\nError Details:');
                results.errorDetails.forEach(error => {
                    console.log(`- ${error.employee} (${error.email}): ${error.error}`);
                });
            }

            return results;

        } catch (error) {
            console.error('Fatal error during provisioning:', error.message);
            throw error;
        }
    }

    /**
     * Sync a single employee by ID
     * @param {string} employeeId - BambooHR employee ID
     */
    async syncSingleEmployee(employeeId) {
        try {
            const response = await this.bambooHRClient.get(`/employees/${employeeId}`, {
                params: {
                    fields: 'firstName,lastName,workEmail,department,jobTitle,employeeNumber,status'
                }
            });

            const employee = response.data;
            
            if (employee.status !== 'Active' || !employee.workEmail) {
                console.log(`Employee ${employeeId} is not active or missing email, skipping...`);
                return;
            }

            const existingUser = await this.checkOktaUserExists(employee.workEmail);
            
            if (existingUser) {
                const updatedProfile = this.createOktaUserProfile(employee).profile;
                await this.updateOktaUser(existingUser.id, updatedProfile);
                console.log(`Updated user: ${employee.workEmail}`);
            } else {
                const userProfile = this.createOktaUserProfile(employee);
                const newUser = await this.createOktaUser(userProfile);
                await this.assignUserToGroups(newUser.id, employee.department, employee.jobTitle);
                console.log(`Created user: ${employee.workEmail}`);
            }

        } catch (error) {
            console.error(`Error syncing employee ${employeeId}:`, error.message);
            throw error;
        }
    }
}

// Usage example
async function main() {
    const bambooHRConfig = {
        subdomain: process.env.BAMBOOHR_SUBDOMAIN || 'your-subdomain',
        apiKey: process.env.BAMBOOHR_API_KEY || 'your-bamboohr-api-key'
    };

    const oktaConfig = {
        domain: process.env.OKTA_DOMAIN || 'your-domain.okta.com',
        apiToken: process.env.OKTA_API_TOKEN || 'your-okta-api-token'
    };

    const provisioner = new BambooHROktaProvisioning(bambooHRConfig, oktaConfig);

    try {
        // Run a dry run first to see what would be processed
        console.log('Running dry run...');
        await provisioner.provisionUsers({ dryRun: true });

        // Uncomment to run actual provisioning
        // console.log('\nRunning actual provisioning...');
        // await provisioner.provisionUsers({ 
        //     dryRun: false, 
        //     updateExisting: true 
        // });

        // Sync a single employee
        // await provisioner.syncSingleEmployee('12345');

    } catch (error) {
        console.error('Provisioning failed:', error.message);
        process.exit(1);
    }
}

// Run the script
if (require.main === module) {
    main();
}

module.exports = BambooHROktaProvisioning;
